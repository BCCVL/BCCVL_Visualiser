import logging
import mimetypes
import urlparse
import urllib
import os
import os.path
from xml.sax.saxutils import escape, quoteattr

import mapscript
import zipfile
from osgeo import gdal
from osgeo.osr import SpatialReference

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.view import view_config, view_defaults

from bccvl_visualiser.utils import fetch_file
from bccvl_visualiser.views import BaseView
from bccvl_visualiser.models.wfs_api import WFSAPI, WFSAPIv1

LOG = logging.getLogger(__name__)


@view_defaults(route_name='wfs_api')
class WFSAPIView(BaseView):
    """The Base WFS API level view '/api/wfs'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(WFSAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(WFSAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(WFSAPIView, self).xmlrpc()

    def _to_dict(self):
        return_dict = {str(k): str(v) for k, v in WFSAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict


@view_defaults(route_name='wfs_api_v1')
class WFSAPIViewv1(WFSAPIView):

    # TODO: probably get rid of this
    _data = None

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(WFSAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(WFSAPIViewv1, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(WFSAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return WFSAPIv1.to_dict()

    @view_config(name='wfs', permission='view')
    def wfs(self):
        """This is a WFS endpoint.

        It uses mapserver mapscript to process a WFS request.

        This endpoint requires an additional WFS parameter
        DATA_URL. The DATA_URL, should point to a downloadable file
        which can be used as raster data input for mapserver.
        """
        LOG.debug('Processing ows request')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            LOG.warn('No data_url provided')
            data_url = None
            # FIXME: should return an error here)

        # get location of local data file
        loc = fetch_file(self.request, data_url)

        # get map
        map = self._get_map()

        # setup layer, only accept zipped shape file.
        # Extract the shape files.
        datadir, filename = os.path.split(loc)
        fname, fext = os.path.splitext(filename)
        if fext == '.zip':
            # Check if shape file exists. If so, already unzip.
            shapeFilename = os.path.join(datadir, fname + ".shp")
            if not ps.path.isFile(shapeFilename):
                with zipfile.ZipFile(loc, 'r') as zipf:
                    zipf.extractall(datadir)
            if os.path.isfile(shapeFilename):
                layer = ShapeLayer(self.request, shapeFilename)
            else:
                msg = "Invalid shape file name '{}'.".format(shapeFilename)           
                raise HTTPNotImplemented(msg)
        else:
            # HTTPBadRequest(msg)
            msg = "Unknown file type '{}'.".format(mimetype)           
            raise HTTPNotImplemented(msg)

        # add the shape layer into map
        idx = layer.add_layer_obj(map)

        # set map projection and extent from layer data
        lx = map.getLayer(idx).getExtent()
        map.extent = mapscript.rectObj(lx.minx, lx.miny, lx.maxx, lx.maxy)
        map.setProjecntion = "init={}".format(layer._data['crs'])

        # prepare an ows request object by copying request params
        ows_req = mapscript.OWSRequest()
        ows_req.loadParamsFromURL(self.request.query_string)

        # here is probably some room for optimisation
        # e.g. let mapscript write directly to output?
        #      write tile to file system and serve tile via some other means?
        #      cache tile or at least mapobj?
        wfs_req = self.request.params['REQUEST']
        wfs_ver = self.request.params.get('VERSION', '1.1.0')

        # now do something based on REQUEST:
        mapscript.msIO_installStdoutToBuffer()
        res = map.OWSDispatch(ows_req)  # if != 0 then error
        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()
        return Response(content, content_type=content_type)
        

    def _get_map(self):
        """
        Generate a mapserver mapObj.
        """
        # create a mapscript map from scratch
        map = mapscript.mapObj()
        # Configure the map
        # NAME
        map.name = "BCCVLMap"
        # EXTENT ... in projection units (we use epsg:4326) WGS84
        map.extent = mapscript.rectObj(-180.0, -90.0, 180.0, 90.0)
        #map.extent = mapscript.rectObj(-20026376.39, -20048966.10, 20026376.39, 20048966.10)
        # UNITS ... in projection units
        map.units = mapscript.MS_DD
        # SIZE
        map.setSize(256, 256)
        # PROJECTION ... WGS84
        map.setProjection("init=epsg:4326")

        # TRANSPARENT ON
        map.transparent = mapscript.MS_ON

        # metadata: wfs_feature_info_mime_type text/htm/ application/json
        # WEB
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        map.setMetaData("wfs_enable_request", "*")
        map.setMetaData("wfs_title", "BCCVL WFS Server")
        map.setMetaData("wfs_srs", "EPSG:4326 EPSG:3857")  # allow reprojection to Web Mercator
        map.setMetaData("ows_enable_request", "*")  # wfs_enable_request enough?
        onlineresource = urlparse.urlunsplit((self.request.scheme,
                                              "{}:{}".format(self.request.host, self.request.host_port),
                                              self.request.path,
                                              urllib.urlencode((('DATA_URL', self.request.params.get('DATA_URL')), ) ),
                                              ""))
        map.setMetaData("wfs_onlineresource", onlineresource)
        # TODO: metadata
        #       title, author, xmp_dc_title
        #       wfs_onlineresource ... help to generate GetCapabilities request
        #       ows_http_max_age ... WFS client caching hints http://www.mnot.net/cache_docs/#CACHE-CONTROL
        #       ows_lsd_enabled ... if false ignore SLD and SLD_BODY
        #       wfs_attribution_xxx ... do we want attribution metadata?

        return map


        # test server (1.1.0 for version support)
        # http://my.host.com/cgi-bin/mapserv?SERVICE=WFS&VERSION=1.1.0&REQUEST=GetCapabilities&DATA_URL=file:///home/visualiser/BCCVL_Visualiser/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/raster.tif

        # test GetFeature
        # http://my.host.com/cgi-bin/mapserv?map=mywfs.map&SERVICE=WFS&VERSION=1.1.0
        # &REQUEST=GetFeature&typeNames=DEFAULT&LAYERS=prov_bound&STYLES=&SRS=EPSG:4326
        # &BBOX=-173.537,35.8775,-11.9603,83.8009&WIDTH=400&HEIGHT=300
        # &FORMAT=image/png


class ShapeLayer(object):

    _data = None

    def __init__(self, request, filename):
        self.request = request
        self.filename = filename

    def _inspect_data(self):
        # TODO: inspect csv, remove invalid values, find extent, and min max values etc...
        self._data = {
            'crs': 'epsg:4326',
        }

        # TODO: find extent using orginfo -al -fid 0

    def add_layer_obj(self, map):
        """
        Create mapserver layer object.

        The raster data for the layer is located at filename, which
        should be an absolute path on the local filesystem.
        """
        # inspect data if we haven't yet
        self._inspect_data()
        # create a layer object
        layer = mapscript.layerObj()
        # configure layer
        # NAME
        layer.name = "DEFAULT"  # TODO: filename?
        # TYPE
        layer.type = mapscript.MS_LAYER_POLYGON
        # STATUS
        layer.status = mapscript.MS_ON
        # mark layer as queryable
        layer.template = "query"  # anything non null and with length > 0 works here

        # DATA
        layer.data = self.filename

        # layer.tolerance = 10.0  # TODO: this should be dynamic based on zoom level
        # layer.toleranceunits = mapscript.MS_PIXELS

        # PROJECTION ... should we ste this properly?
        crs = self._data['crs']
        layer.setProjection("init={}".format(crs))
        # METADATA
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        layer.setMetaData("gml_types", "auto")
        layer.setMetaData("gml_featureid", "id")  # set to segmentNo ??
        layer.setMetaData("gml_include_items", "all")  # allow raster queries
        layer.setMetaData("wfs_include_items", "all")
        layer.setMetaData("wfs_srs", "EPSG:4326 EPSG:3857")  # projection to serve
        layer.setMetaData("wfs_title", "BCCVL Layer")  # title required for GetCapabilities

        # TODO: metadata
        #       other things like title, author, attribution etc...

        return map.insertLayer(layer)

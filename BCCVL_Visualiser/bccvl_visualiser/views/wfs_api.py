import logging
import mimetypes
import urlparse
import urllib
import os
import os.path
import json
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
from bccvl_visualiser.models.external_api import DatabaseManager

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

        # get location of local data file
        if data_url:
            loc = fetch_file(self.request, data_url)

        # get map
        map = self._get_map()

        # Check that appropriate files are already exist.
        datadir, filename = os.path.split(loc)
        fname, fext = os.path.splitext(filename)
        if fext == '.zip':
            # Check if layer mapping file exists.
            mdfile = os.path.join(datadir, 'layer_mappings.json')
            if os.path.isfile(mdfile):
                ds_metadata = json.load(open(mdfile, 'r'))
            else:
                raise HTTPNotImplemented("Missing layer mapping meta data file '{}'".format(mdfile))

            # Check if shape file exists.
            if os.path.isfile(os.path.join(datadir, fname + ".shp")):
                dbFilename = os.path.join(datadir, fname + ".shp")
            elif os.path.isdir(os.path.join(datadir, fname)) and fname.endswith(".gdb"):
                dbFilename = os.path.join(datadir, fname)
            else:
                msg = "Invalid zip file '{}' -- is not in shape/gdb format.".format(filename)
                raise HTTPNotImplemented(msg)
        else:
            raise HTTPNotImplemented("Invalid zip file '{}'".format(filename))

        # if DB server is configured, get layer data from DB server. Otherwise get data from db file.
        layer = ShapeLayer(self.request, dbFilename, ds_metadata)

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

    def __init__(self, request, filename, metadata):
        self.request = request
        self.filename = filename
        self.metadata = metadata

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

        # NAME
        layer.name = "DEFAULT"  # TODO: filename?
        # TYPE
        layer.type = mapscript.MS_LAYER_POLYGON
        # STATUS
        layer.status = mapscript.MS_ON
        # mark layer as queryable
        layer.template = "query"  # anything non null and with length > 0 works here


        # Extract the base table and attribute table from typeNames
        # typeNames = {base_filename}:{{base layername}.{attribute layername}} i.e. stream_attributesv1.1.5.gdb:catchment.climate
        type_name = self.request.params.get('typeNames', None)
        if type_name is None:
            raise Exception("Missing typeNames")

        if type_name.find(":") >= 0:
            filename, layername = type_name.split(':')
        else:
            filename = None
            layername = type_name

        # set layer name
        layer.name = layername

        # Get the corresposning base layer table and attribute table
        #layername = {base layername}.{attribute layername}
        base_layer = None
        if layername.find(".") >= 0:
            base_layer, attr_layer = layername.split('.')
        else:
            # No base layer. Only attribute layer
            attr_layer = layername

        # get the attribute table metadata
        attr_table = None
        if attr_layer:
            layer_info = self.metadata.get('layer_mappings').get(attr_layer, None)
            if layer_info:
                attr_table = layer_info.get('table', None)
        if attr_table is None:
            raise Exception("Invalid typeNames in request: no such layer '{layername}'".format(layername=layername))
        
        # Get the corresposning base table, and its id and geometry column names
        base_table = None
        common_col = None
        if base_layer:
            base_table, id_col, geom_col, extent = self.get_table_details(filename, base_layer)

            if base_table is None or id_col is None or geom_col is None:
                raise Exception("Missing or invalid base table for {layer}".format(layer=base_layer))

            # Get the foreign key i.e. the joinable column
            common_col = self.request.params.get('foreignKey', None)
            if common_col is None:
                raise Exception("Missing foreignKey in request")
        else:
            base_table = attr_table
            layer_info = self.metadata.get('layer_mappings').get(attr_layer, None)
            id_col = layer_info.get('id_column')                # ID column
            geom_col = layer_info.get('geometry_column', None)
            extent = layer_info.get('base_extent', None)
            
        if extent:
            layer.setExtent(extent['xmin'], extent['ymin'], extent['xmax'], extent['ymax'])


        # get the feature ids. It must be in the format: {layername}.fid 
        featureId = self.request.params.get('featureID', '')
        fidlist = featureId.split(',')
        fid = ','.join([v.split('{layername}.'.format(layername=attr_layer))[1] for v in fidlist if len(v.split('.')) > 1])
        if len(fid) == 0:
            fid = None

        # get the attribute names.
        attributeNames = self.request.params.get('attributes', None)

        # DATA, in the format of "<column> from <tablename> using unique fid using srid=xxxx"
        # table must have fid and geom
        # table_attribute in the form 'table-name:attrubute1'
        # TODO: Shall we check that the column and table exists??
        if DatabaseManager.is_configured():
            # Connection to POSTGIS DB server 
            layer.connectiontype = mapscript.MS_POSTGIS
            layer.connection = DatabaseManager.connection_details()

            if attr_table != base_table:
                # Get all attributes of the attribute table if not specified
                if attributeNames is None:
                    fields = [i.lower() for i in self.metadata.get('layer_mappings').get(attr_layer).get('fields')]
                    a_idcol = self.metadata.get('layer_mappings').get(attr_layer).get('id_column')
                    for item in [a_idcol.lower(), common_col.lower()]:
                        if item in fields:
                            fields.remove(item)
                    attributeNames = ','.join(fields)
                if fid:
                    newtable = "(select b.*, {attributes} from {atable} a join {base} b on a.{ccol} = b.{ccol} and b.{idcol} in ({ids}))".format(attributes=attributeNames, atable=attr_table, base=base_table, ccol=common_col, idcol=id_col, ids=fid, geom=geom_col)
                else:
                    newtable = "(select b.*, {attributes} from {atable} a join {base} b on a.{ccol} = b.{ccol})".format(attributes=attributeNames, atable=attr_table, base=base_table, ccol=common_col, idcol=id_col, geom=geom_col)                    
            else:
                if fid:
                    newtable = "(select * from {base} where {idcol} in ({ids}))".format(base=base_table, idcol=id_col, ids=fid)
                else:
                    newtable = "(select * from {base})".format(base=base_table)

            srid = self.request.params.get('SRID', '4326')
            layer.data = "{geom} from {table} as new_layer using unique {idcol} using srid={srid}".format(geom=geom_col, table=newtable, idcol=id_col, srid=srid)

            # Defer closing connection
            layer.addProcessing("CLOSE_CONNECTION=DEFER")

        else:
            # TO DO: read from file
            raise Exception("Database is not configured.")

        # PROJECTION ... should we set this properly?
        crs = self._data['crs']
        layer.setProjection("init={}".format(crs))

        # METADATA
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        layer.setMetaData("gml_types", "auto")
        layer.setMetaData("gml_featureid", id_col) # Shall be the id column of the base table
        layer.setMetaData("gml_include_items", "all")  # allow raster queries
        layer.setMetaData("wfs_include_items", "all")
        layer.setMetaData("wfs_srs", "EPSG:4326 EPSG:3857")  # projection to serve
        layer.setMetaData("wfs_title", "BCCVL Layer")  # title required for GetCapabilities

        # TODO: metadata
        #       other things like title, author, attribution etc...

        return map.insertLayer(layer)

    def get_table_details(self, filename, layername):
        # return table name, id column name, geometry column name, and extent.
        mddata = DatabaseManager.get_metadata(filename)
        if mddata:
            layer_info = mddata.get('layer_mappings').get(layername)
            return (layer_info.get('table', None), layer_info.get('id_column', None), layer_info.get('geometry_column', None), layer_info.get('base_extent', None))
        return (None, None, None, None)
        
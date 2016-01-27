import logging
import mimetypes
import urlparse
import urllib
import os
import os.path

import mapscript
from osgeo import gdal
from osgeo.osr import SpatialReference

from pyramid.response import Response
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.view import view_config, view_defaults

from bccvl_visualiser.utils import fetch_file
from bccvl_visualiser.views import BaseView
from bccvl_visualiser.models.wms_api import WMSAPI, WMSAPIv1

LOG = logging.getLogger(__name__)


@view_defaults(route_name='wms_api')
class WMSAPIView(BaseView):
    """The Base WMS API level view '/api/wms'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(WMSAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(WMSAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(WMSAPIView, self).xmlrpc()

    def _to_dict(self):
        return_dict = {str(k): str(v) for k, v in WMSAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict


@view_defaults(route_name='wms_api_v1')
class WMSAPIViewv1(WMSAPIView):

    # TODO: probably get rid of this
    _data = None

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(WMSAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(WMSAPIViewv1, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(WMSAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return WMSAPIv1.to_dict()

    @view_config(name='wms', permission='view')
    def wms(self):
        """This is a WMS endpoint.

        It uses mapserver mapscript to process a WMS request.

        This endpoint requires an additional WMS parameter
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
        # setup layer
        # TODO: improve selection of Layer generator
        # TODO: use python-magic for a more reliable mime type detection
        mimetype, encoding = mimetypes.guess_type(loc)
        if mimetype == 'image/tiff':
            layer = TiffLayer(self.request, loc)
        elif mimetype == 'text/csv':
            layer = CSVLayer(self.request, loc)
        else:
            msg = "Unknown file type '{}'.".format(mimetype)
            # HTTPBadRequest(msg)
            raise HTTPNotImplemented(msg)
        # add layer into map
        idx = layer.add_layer_obj(map)
        # set map projection and extent from layer data
        lx = map.getLayer(idx).getExtent()
        map.extent = mapscript.rectObj(lx.minx, lx.miny, lx.maxx, lx.maxy)
        map.setProjection = "init={}".format(layer._data['crs'])

        # prepare an ows request object
        # do some map processing here
        ows_req = mapscript.OWSRequest()
        # our layer.add_layer_obj applies SLD and SLD_BODY
        # copy request params into ows request except not these two
        for k, v in ((k, v)for (k, v) in self.request.params.items() if k.lower() not in ('sld', 'sld_body', 'data_url')):
            ows_req.setParameter(k, v)
        # req.setParameter('SERVICE', 'WMS')
        # req.setParameter('VERSION', '1.3.0')
        # req.setParameter('REQUEST', 'GetCapablities')

        # here is probably some room for optimisation
        # e.g. let mapscript write directly to output?
        #      write tile to file system and serve tile via some other means?
        #      cache tile or at least mapobj?
        wms_req = self.request.params['REQUEST']
        wms_ver = self.request.params.get('VERSION', '1.3.0')
        # now do something based on REQUEST:
        if wms_req == u'GetMap':
            res = map.loadOWSParameters(ows_req, wms_ver)  # if != 0 then error
            img = map.draw()
            return Response(img.getBytes(), content_type=img.format.mimetype)
        elif wms_req == u'GetCapabilities':
            mapscript.msIO_installStdoutToBuffer()
            res = map.OWSDispatch(ows_req)  # if != 0 then error
            content_type = mapscript.msIO_stripStdoutBufferContentType()
            content = mapscript.msIO_getStdoutBufferBytes()
            return Response(content, content_type=content_type)
        elif wms_req == u'GetFeatureInfo':
            res = map.loadOWSParameters(ows_req, wms_ver)  # if != 0 then error
            mapscript.msIO_installStdoutToBuffer()
            res = map.OWSDispatch(ows_req)  # if != 0 then error
            content_type = mapscript.msIO_stripStdoutBufferContentType()
            content = mapscript.msIO_getStdoutBufferBytes()
            return Response(content, content_type=content_type)

        # We shouldn't end up here.....
        # let's raise an Error
        # FIXME: I am sure there are better pyramid ways to return errors
        raise Exception('request was not handled correctly')

        # TODO: alternative ways to render map images, and cache on FS
        # my_image =  map.draw() ... render map to image
        # map_image.save(file name) ... store on FS
        # map_image.format.mime_type ... get image mime type
        # map_image.format.extension ... typical file extension for image type
        # map_image.write() ... write file handle (default stdeout)

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
        # IMAGETYPE
        map.selectOutputFormat("PNG24")  # PNG, PNG24, JPEG
        map.outputformat.imagemode = mapscript.MS_IMAGEMODE_RGBA
        map.outputformat.transparent = mapscript.MS_ON

        # TRANSPARENT ON
        map.transparent = mapscript.MS_ON
        # IMAGECOLOR 255 255 255
        # map.imagecolor = mapscript.colorObj(255, 255, 255) ... initial color if transparent is on
        # SYMBOLSET  (needed to draw circles for CSV points)
        self._update_symbol_set(map)
        # metadata: wms_feature_info_mime_type text/htm/ application/json
        # WEB
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        map.setMetaData("wms_enable_request", "*")
        map.setMetaData("wms_title", "BCCVL WMS Server")
        map.setMetaData("wms_srs", "EPSG:4326 EPSG:3857")  # allow reprojection to Web Mercator
        map.setMetaData("ows_enable_request", "*")  # wms_enable_request enough?
        onlineresource = urlparse.urlunsplit((self.request.scheme,
                                              "{}:{}".format(self.request.host, self.request.host_port),
                                              self.request.path,
                                              urllib.urlencode((('DATA_URL', self.request.params.get('DATA_URL')), ) ),
                                              ""))
        map.setMetaData("wms_onlineresource", onlineresource)
        # TODO: metadata
        #       title, author, xmp_dc_title
        #       wms_onlineresource ... help to generate GetCapabilities request
        #       ows_http_max_age ... WMS client caching hints http://www.mnot.net/cache_docs/#CACHE-CONTROL
        #       ows_lsd_enabled ... if false ignore SLD and SLD_BODY
        #       wms_attribution_xxx ... do we want attribution metadata?

        # SCALEBAR
        if False:
            # LABEL
            sbl = mapscript.labelObj()
            sbl.color = mapscript.colorObj(0, 0, 0)
            sbl.antialias = mapscript.MS_TRUE
            sbl.size = mapscript.MS_LARGE
            sb = mapscript.scalebarObj()
            sb.label = sbl
            sb.status = mapscript.MS_ON
            map.scalebar = sb
        # LEGEND
        if False:
            # LABEL
            legl = mapscript.labelObj()
            legl.color = mapscript.colorObj(64, 64, 64)
            legl.antialias = mapscript.MS_TRUE
            legl.offsetx = -23
            legl.offsety = -1
            leg = mapscript.legendObj()
            leg.keysizex = 32
            leg.keysizey = 10
            leg.keyspacingx = 5
            leg.keyspacingy = -2
            leg.status = mapscript.MS_ON
            map.legend = leg
        return map

    def _update_symbol_set(self, map):
        circle = map.symbolset.getSymbolByName('circle')
        # circle = mapscript.symbolObj("circle")
        circle.type = mapscript.MS_SYMBOL_ELLIPSE
        circle.filled = mapscript.MS_ON
        l1 = mapscript.lineObj()
        l1.add(mapscript.pointObj(1, 1))
        circle.setPoints(l1)
        map.symbolset.appendSymbol(circle)

        # test server (1.3.0 for SLD support)
        # http://my.host.com/cgi-bin/mapserv?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetCapabilities&DATA_URL=file:///home/visualiser/BCCVL_Visualiser/BCCVL_Visualiser/bccvl_visualiser/tests/fixtures/raster.tif

        # test map
        # http://my.host.com/cgi-bin/mapserv?map=mywms.map&SERVICE=WMS&VERSION=1.1.1
        # &REQUEST=GetMap&LAYERS=prov_bound&STYLES=&SRS=EPSG:4326
        # &BBOX=-173.537,35.8775,-11.9603,83.8009&WIDTH=400&HEIGHT=300
        # &FORMAT=image/png

        # # TODO: spped up large rasters?
        #     http://mapserver.org/el/input/raster.html#rasters-and-tile-indexing

        # TODO: FONTSET [filename]
        #    set location of fontset file http://mapserver.org/el/mapfile/fontset.html


class TiffLayer(object):

    _data = None

    def __init__(self, request, filename):
        self.request = request
        self.filename = filename

    def _inspect_data(self):
        """
        Extract coordinate reference system and min/max values from a
        GDAL supported raster data file.
        """

        if self._data is None:
            # TODO: This method is really ugly, but is nice for testing
            self._data = {}
            df = gdal.Open(self.filename)
            # TODO: df may be None?
            crs = df.GetProjection()
            if crs:
                spref = SpatialReference(wkt=crs)
                # default to epsg:4326
                auth = spref.GetAuthorityName(None) or 'epsg'
                code = spref.GetAuthorityCode(None) or '4326'
                self._data['crs'] = "%s:%s" %  (auth.lower(), code)
                #LOG.info('Detected CRS: %s', self._data['crs'])
            else:
                self._data['crs'] = 'epsg:4326'  # use epsg:4326 as default
            band = df.GetRasterBand(1)
            self._data['min'], self._data['max'], _, _ = band.GetStatistics(True, False)
            self._data['nodata'] = band.GetNoDataValue()
            self._data['datatype'] = band.DataType

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
        layer.name = "DEFAULT"  # TODO: filename?, real title?
        # TYPE
        layer.type = mapscript.MS_LAYER_RASTER
        # STATUS
        layer.status = mapscript.MS_ON
        # mark layer as queryable
        layer.template = "dummy"  # anything non null and with length > 0 works here
        # CONNECTION_TYPE local|ogr?
        # layer.setConnectionType(MS_RASTER) MS_OGR?
        # DATA
        layer.data = self.filename

        layer.tolerance = 10.0  # TODO: this should be dynamic based on zoom level
        # layer.toleranceunits = mapscript.MS_PIXELS

        # PROJECTION ... should we ste this properly?
        crs = self._data['crs']
        layer.setProjection("init={}".format(crs))
        # METADATA
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        layer.setMetaData("gml_include_items", "all")  # allow raster queries
        layer.setMetaData("wms_include_items", "all")
        layer.setMetaData("wms_srs", "{}".format(crs))
        layer.setMetaData("wms_title", "BCCVL Layer")  # title required for GetCapabilities
        # TODO: metadata
        #       other things like title, author, attribution etc...
        # OPACITY
        # TODO: this should probably be up to the client?
        # layer.setOpacity(70)

        # If data type is not integer:
        if self._data['datatype'] not in (gdal.GDT_Byte, gdal.GDT_UInt16, gdal.GDT_Int16,
                                          gdal.GDT_UInt32, gdal.GDT_Int32):
            # mapservers does the right thing with these processing instructions
            # setting scale, skips the integer processing step and reads the raster
            # as float
            layer.addProcessing("SCALE=AUTO,AUTO")
            layer.addProcessing("NODATA=AUTO")

        # CLASSITEM, CLASS
        # TODO: if we have a STYLES parameter we should add a STYLES element here
        if not (self.request.params.get('STYLES') or
                'SLD' in self.request.params or
                'SLD_BODY' in self.request.params):
            # set some default style if the user didn't specify any'
            # STYLE
            styleobj = mapscript.styleObj()
            styleobj.mincolor = mapscript.colorObj(255, 255, 255)
            styleobj.maxcolor = mapscript.colorObj(0, 128, 255)
            if self._data:
                styleobj.minvalue = self._data['min']
                styleobj.maxvalue = self._data['max']
            styleobj.rangeitem = "[pixel]"
            clsobj = mapscript.classObj()
            clsobj.name = "-"
            # clsobj.setExpression("([pixel]>0)")
            clsobj.insertStyle(styleobj)
            # layer.classitem = "[pixel]"
            layer.insertClass(clsobj)

        ret = map.insertLayer(layer)

        sld = self.request.params.get('SLD_BODY')
        sld_url = self.request.params.get('SLD')
        if sld_url:
            map.applySLDURL(sld_url)
        elif sld:
            map.applySLD(sld)
        if ((sld or sld_url) and (self._data['datatype'] == gdal.GDT_Byte and self._data['nodata'] is not None)):
            # if we have 8bit data, mapserver ignores the NODATA value, so let's classify it as transparent
            styleobj = mapscript.styleObj()
            styleobj.color = mapscript.colorObj(0, 0, 0, 0)
            styleobj.rangeitem = "[pixel]"
            clsobj = mapscript.classObj()
            clsobj.name = 'NODATA'
            clsobj.setExpression("([pixel] = {})".format(int(self._data['nodata'])))
            clsobj.insertStyle(styleobj)
            layer.insertClass(clsobj, 0)

        return ret


class CSVLayer(object):

    _data = None

    def __init__(self, request, filename):
        self.request = request
        self.filename = filename

    def _inspect_data(self):
        # TODO: inspect csv, remove invalid values, find extent, and min max values etc...
        self._data = {
            'crs': 'epsg:4326',
        }

    def add_layer_obj(self, map):
        """Create mapserver layer object.

        The data is assumed to be a csv file with column 'lon' and
        'lat' describing ponit features.
        """
        # inspect data if we haven't yet
        self._inspect_data()
        # create a layer object
        layer = mapscript.layerObj()
        # configure layer
        # NAME
        layer.name = "DEFAULT"  # TODO: filename?, real title?
        # TYPE
        # TODO: this supports only POINT datasets for now,... should detect this somehow
        layer.type = mapscript.MS_LAYER_POINT
        # STATUS
        layer.status = mapscript.MS_ON
        # mark layer as queryable
        layer.template = "query"  # anything non null and with length > 0 works here
        # CONNECTION_TYPE local|ogr?
        layer.setConnectionType(mapscript.MS_OGR, None)
        # TODO: the VRT source works fine, but maybe converting the VRT to a real shapefile with ogr2ogr would spped up rendering? (or use a sqlite/spatiallite datasource?)
        # TODO: check if GDAL dies and kills whole mapserver process in case the csv file is not valid or contains broken values
        # layer.setConnectionType(MS_RASTER) MS_OGR?
        # TODO: other elements to consider:
        #        Metadata ... on Datasource and LAyer
        #        OpenOptions ... only gdal >= 2.0
        #        FID ... ??
        #        Style ... ???
        #        FeatureCount
        #        ExtentXMien, ExtentXMax, ExtentYMin, ExtentYMax
        layer.connection = """"\
<OGRVRTDataSource>
    <OGRVRTLayer name='{0}'>
        <SrcDataSource>{1}</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <LayerSRS>EPSG:4326</LayerSRS>
        <GeometryField name='location' encoding='PointFromColumns' x='lon' y='lat'/>
    </OGRVRTLayer>
</OGRVRTDataSource>""".format(os.path.splitext(os.path.basename(self.filename))[0], self.filename)
        # PROJECTION ... should we ste this properly?
        # TODO: this always assume epsg:4326
        layer.setProjection("init={}".format(self._data['crs']))
        # METADATA
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        layer.setMetaData("gml_include_items", "all")
        layer.setMetaData("wms_include_items", "all")
        layer.setMetaData("wms_title", "BCCVL Occurrences")
        layer.setMetaData("wms_srs", self._data['crs'])  # can be a space separated list
        # TODO: metadata
        #       other things like title, author, attribution etc...
        if not (self.request.params.get('STYLES') or
                'SLD' in self.request.params or
                'SLD_BODY' in self.request.params):
            # set some default style if the user didn't specify any'
            # STYLE
            styleobj = mapscript.styleObj()
            styleobj.color = mapscript.colorObj(255, 50, 50)
            styleobj.minsize = 2
            styleobj.maxsize = 50
            styleobj.size = 5
            styleobj.symbol = map.symbolset.index('circle')
            clsobj = mapscript.classObj()
            clsobj.name = "record"
            clsobj.insertStyle(styleobj)
            layer.insertClass(clsobj)

        ret = map.insertLayer(layer)
        # apply SLD if given
        sld = self.request.params.get('SLD_BODY')
        sld_url = self.request.params.get('SLD')
        if sld_url:
            map.applySLDURL(sld_url)
        elif sld:
            map.applySLD(sld)

        return ret

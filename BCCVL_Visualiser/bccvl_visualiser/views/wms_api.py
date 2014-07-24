import logging
import mapscript
import urlparse
import hashlib
import os.path
import zipfile
import urllib

from pyramid.response import Response
from pyramid.view import view_config, view_defaults

from bccvl_visualiser.models.external_api.data_mover import FDataMover
from bccvl_visualiser.models.bccvl_map import LockFile
from bccvl_visualiser.views import BaseView
from bccvl_visualiser.models.wms_api import WMSAPI, WMSAPIv1


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

    @view_config(name='wms')
    def wms(self):
        """This is a WMS endpoint.

        It uses mapserver mapscript to process a WMS request.

        This endpoint requires an additional WMS parameter
        DATA_URL. The DATA_URL, should point to a downloadable file
        which can be used as raster data input for mapserver.
        """
        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            log.warn('No data_url provided')
            data_url = None
            # FIXME: should return an error here)

        # get location of local data file
        loc = self._fetch_file(data_url)
        # get some metadata if possible
        self._inspect_data(loc)
        # get map
        map = self._get_map()
        # setup layer
        self._setup_layer(map, loc)

        # prepare an ows request object
        # do some map processing here
        req = mapscript.OWSRequest()
        req.loadParamsFromURL(self.request.query_string.strip())
        # req.setParameter('SERVICE', 'WMS')
        # req.setParameter('VERSION', '1.3.0')
        # req.setParameter('REQUEST', 'GetCapablities')

        # here is probably some room for optimisation
        # e.g. let mapscript write directly to output?
        #      write tile to file system and serve tile via some other means?

        # Let's do some standard mapscripm dispatch for now
        mapscript.msIO_installStdoutToBuffer()
        # TODO: check retval for mapscript.MS_SUCCESS
        retval = map.OWSDispatch(req)
        content_type = mapscript.msIO_stripStdoutBufferContentType()
        content = mapscript.msIO_getStdoutBufferBytes()
        mapscript.msIO_resetHandlers()

        # return a pyramid response
        return Response(content, content_type=content_type)

        # TODO: alternative ways to render map images
        # my_image =  map.draw() ... render map to image
        # map_image.save(file name) ... store on FS
        # map_image.format.mime_type ... get image mime type
        # map_image.format.extension ... typical file extension for image type
        # map_image.write() ... write file handle (default stdeout)

    def _inspect_data(self, loc):
        """
        Extract coordinate reference system and min/max values from a
        GDAL supported raster data file.
        """
        # TODO: This method is really ugly, but is nice for testing
        from osgeo import gdal
        from osgeo.osr import SpatialReference
        df = gdal.Open(loc)
        crs = df.GetProjection()
        if crs:
            spref = SpatialReference()
            spref.ImportFromWkt(crs)
            crs = "%s:%s" %  (spref.GetAuthorityName(None), spref.GetAuthorityCode(None))
        band = df.GetRasterBand(1)
        min, max, _, _ = band.GetStatistics(True, False)
        self._data = {
            'crs': crs,
            'min': min,
            'max': max
        }

    # FIXME: for large files we probably have to mave the file transfer to some other process...
    #        something similar to the data mover interface.
    #        e.g download, extract, optimise ....  when ready tell
    #            UI OK ... otherwise tell progress and pending
    def _fetch_file(self, url):
        """Dowload the file from url and place it on the local file system.
        If file is a zip file it will be extracted to the local file system.

        The method returns the filename of the requested file on the
        local file system.
        """
        # TODO: optimize  data files for mapserver?
        # reproject/warp source? to avoid mapserver doing warp on the fly
        # otheroptions:
        #   convert to tiled raster (makes access to tiles faster)
        #     gdal_translate -co TILED=YES original.tif tiled.tif
        #   use Erdas Imagine (HFA) format ... always tiled and supports>4GB files
        #     gdal_translate -of HFA original.tif tiled.img
        #   add overview image to raster (after possible translate)
        #     gdaladdo [-r average] tiled.tif 2 4 8 16 32 64 128

        # get fragment identifier and hash url without fragment
        if not (url.startswith('http://') or url.startswith('https://')):
            # TODO: probably allow more than just http and https
            #       and use better exception
           raise Exception('unsupported url scheme: %s', url)
        url, fragment = urlparse.urldefrag(url)
        # TODO: would be nice to use datasetid here
        urlhash = hashlib.md5(url).hexdigest()
        # check if we have the file already
        dataroot = self.request.registry.settings['bccvl.mapscript.map_data_files_root_path']
        datadir = os.path.join(dataroot, urlhash)
        with LockFile(datadir + '.lock'):
            if not os.path.exists(datadir):
                # the folder doesn't exist so we'll have to fetch the file
                # TODO: make sure there is no '..' in datadir
                os.makedirs(datadir)
                # not available yet so fetch it
                destfile = os.path.join(datadir, os.path.basename(url))
                try:
                    f, h = urllib.urlretrieve(url, destfile)
                except Exception as e:
                    # direct download failed try data mover
                    mover = FDataMover.new_data_mover(destfile,
                                                      data_url=url)
                    mover.move_and_wait_for_completion()
                # if it is a zip we should unpack it
                # FIXME: do some more robust zip detection
                if fragment:
                    with zipfile.ZipFile(destfile, 'r') as zipf:
                        zipf.extractall(datadir)
                    # remove zipfile
                    os.remove(destfile)
        # we have the data now construct the filepath
        filename = fragment if fragment else os.path.basename(url)
        # FIXME: make sure path.join works correctly (trailing/leading slash?)
        filename = os.path.join(datadir, filename)
        # make sure filename is within datadir
        filename = os.path.normpath(filename)
        if not os.path.normpath(filename).startswith(datadir):
            # FIXME: should probably check if filename exists and is supported
            #        and use better exception here
            raise Exception("Data file path not valid: '%s'", filename)
        return filename

    def _get_map(self):
        """
        Generate a mapserver mapObj.
        """
        # create a mapscript map from scratch
        map = mapscript.mapObj()
        # Configure the map
        # NAME
        map.name = "BCCVL Map"
        # EXTENT ... in projection units
        map.extent = mapscript.rectObj(-180.0, -90.0, 180.0, 90.0)
        # UNITS ... in projection units
        map.units = mapscript.MS_DD
        # SIZE
        map.setSize(256, 256)
        # PROJECTION ... web mercator/ Google mercator
        # TODO: woulde epsg:3395 be an alternative?
        map.setProjection("init=epsg:3857")
        # IMAGETYPE
        map.selectOutputFormat("PNG")  # PNG, PNG24, JPEG
        # TRANSPARENT ON
        map.transparent = mapscript.MS_ON
        # IMAGECOLOR 255 255 255
        map.imagecolor = mapscript.colorObj(255, 255, 255)
        # TODO:
        #   SCALEBAR

        # WEB
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        map.setMetaData("wms_enable_request", "GetCapabilities GetMap")
        map.setMetaData("wms_title", "BCCVL WMS Server")
        map.setMetaData("wms_srs", "EPSG:3857")  # can be a space separated list
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
        if True:
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
        if True:
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

    def _setup_layer(self, map, filename):
        """Add a Layer definition to the mapserver mapObj.

        The raster data for the layer is located at filename, which
        should be an absolute path on the local filesystem.
        """
        # create a layer object
        layer = mapscript.layerObj()
        # configure layer
        # NAME
        layer.name = "DEFAULT"  # TODO: filename?, real title?
        # TYPE
        layer.type = mapscript.MS_LAYER_RASTER
        # STATUS
        layer.status =  mapscript.MS_ON
        # CONNECTION_TYPE local|ogr?
        # layer.setConnectionType(MS_RASTER) MS_OGR?
        # DATA
        layer.data = filename
        # PROJECTION ... should we ste this properly?
        if self._data.get('crs'):
            # our dataset has a projection set, let mapserver use it
            layer.setProjection("AUTO")
        else:
            # otherwise assume epsg:4326
            layer.setProjection("init=epsg:4326")
        # METADATA
        # TODO: check return value of setMetaData MS_SUCCESS/MS_FAILURE
        #map.setMetaData("wms_enable_request", "GetCapabilities GetMap")
        #map.setMetaData("wms_title", "BCCVL WMS Server")
        #map.setMetaData("wms_srs", "EPSG:3857")  # can be a space separated list
        # TODO: metadata
        #       other things like title, author, attribution etc...
        # OPACITY
        # TODO: this should probably be up to the client?
        layer.opacity = 70
        # CLASSITEM, CLASS
        # TODO: if we have a STYLES parameter we should add a STYLES element here
        if not ('STYLES' in self.request.params or
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
            styleobj.rangetime = "[pixel]"
            clsobj = mapscript.classObj()
            clsobj.name = "-"
            #clsobj.setExpression("([pixel]>0)")
            clsobj.insertStyle(styleobj)
            #layer.classitem = "[pixel]"
            layer.insertClass(clsobj)

        # add layer into map
        idx = map.insertLayer(layer)
        return idx


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

import logging
import tempfile
import mapscript
import threading

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_xmlrpc import *

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import *
from bccvl_visualiser.views import BaseView

MAPSCRIPT_RLOCK = threading.RLock()


@view_defaults(route_name='raster_api')
class BaseRasterAPIView(BaseView):
    """The Base Raster API level view '/api/raster'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self.to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BaseRasterAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BaseRasterAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BaseRasterAPIView, self).xmlrpc()

    def _to_dict(self):
        return BaseRasterAPI.get_human_readable_inheritors_version_dict()

@view_defaults(route_name='raster_api_v1')
class RasterAPIViewv1(BaseRasterAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(RasterAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(RasterAPIViewv1, self).text()

    @view_config(name='demo_map', renderer='../templates/api/raster/v1/demo_map.pt')
    def demo_map(self):
        return self._to_dict()

    @view_config(name='wms')
    def wms(self):

        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_id = None
        try:
            data_id = self.request.GET.getone('data_id')
        except:
            log.warn('No data_id provided')
            data_id = None

        map, ows_request = RasterAPIv1.\
            get_map_and_ows_request_from_from_request(self.request)

        # Set the data for the first layer specified (unless already set)
        layers = ows_request.getValueByName('LAYERS')
        layer_name = layers.split(',')[0]
        RasterAPIv1.set_data_for_map_layer_if_not_set(map, None, layer_name)

        map_image = None
        map_image_content_type = None

        with MAPSCRIPT_RLOCK:
            mapscript.msIO_installStdoutToBuffer()
            retval = map.OWSDispatch(ows_request)
            map_image_content_type = mapscript.msIO_stripStdoutBufferContentType()
            map_image = mapscript.msIO_getStdoutBufferBytes()
            mapscript.msIO_resetHandlers()

        response = Response(map_image, content_type=map_image_content_type)

        # log.debug("Map Content Type: %s", map_image_content_type)
        # log.debug("Map Contents:\n%s", map_image)

#        image_obj = map.draw()
#        tf = tempfile.NamedTemporaryFile()
#        log.debug('tempfile %s', tf)
#        path = os.path.abspath(tf.name)
#        image_obj.save(path)
#        response = FileResponse(path, request=self.request, content_type='image/jpeg')
#
        return response

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(RasterAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return RasterAPIv1.to_dict()

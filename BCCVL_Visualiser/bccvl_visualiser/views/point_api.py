import logging
import tempfile
import mapscript

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_xmlrpc import *

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import *
from bccvl_visualiser.views import BaseView



@view_defaults(route_name='point_api')
class BasePointAPIView(BaseView):
    """The Base Point API level view '/api/point'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self.to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BasePointAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BasePointAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BasePointAPIView, self).xmlrpc()

    def _to_dict(self):
        return BasePointAPI.get_human_readable_inheritors_version_dict()

@view_defaults(route_name='point_api_v1')
class PointAPIViewv1(BasePointAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(PointAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(PointAPIViewv1, self).text()

    @view_config(name='demo_map', renderer='../templates/api/point/v1/demo_map.pt')
    def demo_map(self):
        return self._to_dict()

    @view_config(name='data_url_map', renderer='../templates/api/point/v1/data_url_map.pt')
    def data_url_map(self):
        return_dict = {
            "data_url": self.request.GET.getone('data_url'),
        }
        return return_dict

    # Cache this view for 1 day (86400 seconds)
    @view_config(name='wms', http_cache=86400)
    def wms(self):

        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_id = None
        try:
            data_id = self.request.GET.getone('data_id')
        except:
            log.warn('No data_id provided')
            data_id = None

        map, ows_request = PointAPIv1.\
            get_map_and_ows_request_from_request(self.request)

        # Set the data for the first layer specified (unless already set)
        layers = ows_request.getValueByName('LAYERS')
        layer_name = layers.split(',')[0]

        PointAPIv1.set_connection_for_map_connection_if_not_set(self.request, map, data_id, layer_name)

        map_image = None
        map_image_content_type = None

        with MapScriptHelper.MAPSCRIPT_RLOCK:
            mapscript.msIO_installStdoutToBuffer()
            retval = map.OWSDispatch(ows_request)
            map_image_content_type = mapscript.msIO_stripStdoutBufferContentType()
            map_image = mapscript.msIO_getStdoutBufferBytes()
            mapscript.msIO_resetHandlers()

        response = Response(map_image, content_type=map_image_content_type)

        return response

    # Cache this view for 1 day (86400 seconds)
    @view_config(name='wms_data_url', http_cache=86400)
    def wms_data_url(self):

        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            log.warn('No data_url provided')
            data_url = None

        map, ows_request = PointAPIv1.\
            get_map_and_ows_request_from_request(self.request)

        # Set the data for the first layer specified (unless already set)
        layers = ows_request.getValueByName('LAYERS')
        layer_name = layers.split(',')[0]

        PointAPIv1.set_connection_for_map_connection_if_not_set_url(self.request, map, data_url, layer_name)

        map_image = None
        map_image_content_type = None

        with MapScriptHelper.MAPSCRIPT_RLOCK:
            mapscript.msIO_installStdoutToBuffer()
            retval = map.OWSDispatch(ows_request)
            map_image_content_type = mapscript.msIO_stripStdoutBufferContentType()
            map_image = mapscript.msIO_getStdoutBufferBytes()
            mapscript.msIO_resetHandlers()

        response = Response(map_image, content_type=map_image_content_type)

        return response

    # Cache this view for 1 day (86400 seconds)
    @view_config(name='wfs', http_cache=86400)
    def wfs(self):

        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_id = None
        try:
            data_id = self.request.GET.getone('data_id')
        except:
            log.warn('No data_id provided')
            data_id = None

        map, ows_request = PointAPIv1.\
            get_map_and_ows_request_from_request(self.request)

        # Set the data for the first layer specified (unless already set)
        layer_name = ows_request.getValueByName('LAYER')
        PointAPIv1.set_connection_for_map_connection_if_not_set(self.request, map, data_id, layer_name)

        map_image = None
        map_image_content_type = None

        with MapScriptHelper.MAPSCRIPT_RLOCK:
            mapscript.msIO_installStdoutToBuffer()
            retval = map.OWSDispatch(ows_request)
            map_image_content_type = mapscript.msIO_stripStdoutBufferContentType()
            map_image = mapscript.msIO_getStdoutBufferBytes()
            mapscript.msIO_resetHandlers()

        response = Response(map_image, content_type=map_image_content_type)

        return response

    # Cache this view for 1 day (86400 seconds)
    @view_config(name='wfs_data_url', http_cache=86400)
    def wfs_data_url(self):

        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            log.warn('No data_url provided')
            data_url = None

        map, ows_request = PointAPIv1.\
            get_map_and_ows_request_from_request(self.request)

        # Set the data for the first layer specified (unless already set)
        layer_name = ows_request.getValueByName('LAYER')
        PointAPIv1.set_connection_for_map_connection_if_not_set_url(self.request, map, data_url, layer_name)

        map_image = None
        map_image_content_type = None

        with MapScriptHelper.MAPSCRIPT_RLOCK:
            mapscript.msIO_installStdoutToBuffer()
            retval = map.OWSDispatch(ows_request)
            map_image_content_type = mapscript.msIO_stripStdoutBufferContentType()
            map_image = mapscript.msIO_getStdoutBufferBytes()
            mapscript.msIO_resetHandlers()

        response = Response(map_image, content_type=map_image_content_type)

        return response

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(PointAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return PointAPIv1.to_dict()

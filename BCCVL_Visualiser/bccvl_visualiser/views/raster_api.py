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


@view_defaults(route_name='raster_api')
class BaseRasterAPIView(BaseView):
    """The Base Raster API level view '/api/raster'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

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
        return_dict = {str(k): str(v) for k, v in BaseRasterAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict

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


    @view_config(name='data_url_map', renderer='../templates/api/raster/v1/data_url_map.pt')
    @view_config(name='default', renderer='../templates/api/raster/v1/data_url_map.pt')
    def data_url_map(self):
        return_dict = {
            "data_url": self.request.GET.getone('data_url'),
        }
        return return_dict

    @view_config(name='map', renderer='../templates/api/raster/v1/map.pt')
    def map(self):
        return_dict = {
            "data_ids": self.request.GET.getone('data_ids').split(','),
        }
        return return_dict

    @view_config(name='wms_data_url')
    def wms_data_url(self):
        log = logging.getLogger(__name__)
        log.debug('Processing ows request')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            log.warn('No data_url provided')
            data_url = None

        my_map = RasterAPIv1(data_url=data_url, query_string=self.request.query_string.strip())
        map_content, map_content_type, retval = my_map.render()

        response = Response(map_content, content_type=map_content_type)

        return response

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

        my_map = RasterAPIv1(data_id=data_id, query_string=self.request.query_string.strip())
        map_content, map_content_type, retval = my_map.render()

        response = Response(map_content, content_type=map_content_type)

        return response

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(RasterAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return RasterAPIv1.to_dict()

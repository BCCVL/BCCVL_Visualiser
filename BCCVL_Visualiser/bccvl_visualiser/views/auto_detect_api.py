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

@view_defaults(route_name='auto_detect_api')
class BaseAutoDetectAPIView(BaseView):
    """The Base AutoDetect API level view '/api/auto_detect'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self.to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BaseAutoDetectAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BaseAutoDetectAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BaseAutoDetectAPIView, self).xmlrpc()

    def _to_dict(self):
        return BaseAutoDetectAPI.get_human_readable_inheritors_version_dict()

@view_defaults(route_name='auto_detect_api_v1')
class AutoDetectAPIViewv1(BaseAutoDetectAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(AutoDetectAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(AutoDetectAPIViewv1, self).text()

    @view_config(name='default')
    def default(self):
        data_url = self.request.GET.getone('data_url')
        url = ''

        if data_url.endswith('.csv'):
            url = self.request.route_url('point_api_v1', traverse='/data_url_map', _query=self.request.GET)
        elif data_url.endswith('.tif'):
            url = self.request.route_url('raster_api_v1', traverse='/data_url_map', _query=self.request.GET)
        else:
            url = self.request.route_url('r_api_v1', traverse='/data_url_view', _query=self.request.GET)

        return HTTPFound(location=url)

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(AutoDetectAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return AutoDetectAPIv1.to_dict()

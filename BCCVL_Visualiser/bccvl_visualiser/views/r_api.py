import logging
import tempfile
import mapscript
import requests

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_xmlrpc import *

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import RAPIv1
from bccvl_visualiser.views import BaseView



@view_defaults(route_name='r_api')
class BaseRAPIView(BaseView):
    """The Base R API level view '/api/r'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self.to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BaseRAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BaseRAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BaseRAPIView, self).xmlrpc()

    def _to_dict(self):
        return BaseRAPI.get_human_readable_inheritors_version_dict()

@view_defaults(route_name='r_api_v1')
class RAPIViewv1(BaseRAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(RAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(RAPIViewv1, self).text()

    # Cache this view for 1 day (86400 seconds)
    @view_config(name='view_data_url', renderer='../templates/api/r/v1/view.pt', http_cache=86400)
    def view(self):

        log = logging.getLogger(__name__)
        log.debug('Processing view request in R API v1')

        data_url = None
        try:
            data_url = self.request.GET.getone('DATA_URL')
        except:
            log.warn('No data_url provided')
            data_url = None

        r = requests.get(data_url, verify=False)
        r.raise_for_status()

        return { 'file_content': r.content.decode('utf-8') }

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(RAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return RAPIv1.to_dict()

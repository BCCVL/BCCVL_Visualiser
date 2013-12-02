import logging
import tempfile
import mapscript
import os

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import RAPIv1, BaseRAPI, FDataMover
from bccvl_visualiser.views import BaseView



@view_defaults(route_name='r_api')
class BaseRAPIView(BaseView):
    """The Base R API level view '/api/r'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

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
        return_dict = {str(k): str(v) for k, v in BaseRAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict

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

    @view_config(name='data_url_view', renderer='../templates/api/r/v1/view.pt')
    @view_config(name='default', renderer='../templates/api/r/v1/view.pt')
    def view(self):

        log = logging.getLogger(__name__)
        log.debug('Processing view request in R API v1')

        data_url = self.request.GET.getone('data_url')

        MyDataMover = FDataMover.get_data_mover_class()
        content = None
        with MyDataMover.open(data_url=data_url) as f:
            content = f.read()

        return { 'file_content': content.encode('ascii', 'replace') }

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(RAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return RAPIv1.to_dict()

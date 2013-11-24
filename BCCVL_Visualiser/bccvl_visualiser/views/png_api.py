import logging
import tempfile
import mapscript
import requests

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import PNGAPIv1
from bccvl_visualiser.views import BaseView



@view_defaults(route_name='png_api')
class BasePNGAPIView(BaseView):
    """The Base PNG API level view '/api/r'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BasePNGAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BasePNGAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BasePNGAPIView, self).xmlrpc()

    def _to_dict(self):
        return_dict = {str(k): str(v) for k, v in BasePNGAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict

@view_defaults(route_name='png_api_v1')
class PNGAPIViewv1(BasePNGAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(PNGAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(PNGAPIViewv1, self).text()

    @view_config(name='data_url_view')
    @view_config(name='default')
    def view(self):

        log = logging.getLogger(__name__)
        log.debug('Processing view request in PNG API v1')

        data_url = self.request.GET.getone('data_url')

        r = requests.get(data_url, verify=False)
        r.raise_for_status()

        response = Response(r.content, content_type=r.headers['content-type'])
        return response

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(PNGAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return PNGAPIv1.to_dict()

import logging
import tempfile
import mapscript
import requests

from pyramid.response import Response, FileResponse
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from bccvl_visualiser.models import BaseHTMLAPI, HTMLAPIv1
from bccvl_visualiser.views import BaseView

@view_defaults(route_name='html_api')
class BaseHTMLAPIView(BaseView):
    """The Base HTML API level view '/api/html'"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(BaseHTMLAPIView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(BaseHTMLAPIView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(BaseHTMLAPIView, self).xmlrpc()

    def _to_dict(self):
        return_dict = {str(k): str(v) for k, v in BaseHTMLAPI.get_human_readable_inheritors_version_dict().items()}
        return return_dict

@view_defaults(route_name='html_api_v1')
class HTMLAPIViewv1(BaseHTMLAPIView):

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(HTMLAPIViewv1, self).json()

    @view_config(name='.text')
    def text(self):
        return super(HTMLAPIViewv1, self).text()

    @view_config(name='data_url_view')
    @view_config(name='default')
    def view(self):

        log = logging.getLogger(__name__)
        log.debug('Processing view request in HTML API v1')

        data_url = self.request.GET.getone('data_url')

        r = requests.get(data_url, verify=False)
        r.raise_for_status()

        content = r.content
        out_str = HTMLAPIv1.replace_urls(content, data_url)

        response = Response(out_str, content_type="text/html")
        return response

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(HTMLAPIViewv1, self).xmlrpc()

    def _to_dict(self):
        return HTMLAPIv1.to_dict()

from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_xmlrpc import *

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import (
    APICollection
    )

from bccvl_visualiser.views import BaseView

import logging

@view_defaults(route_name='api')
class ApiView(BaseView):
    """The API level view"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        """Return the APIs avaialble in JSON"""

        log = logging.getLogger(__name__)
        log.debug('API JSON Request')

        return self._to_dict()

    @view_config(name='.text')
    def text(self):
        """Return the APIs avaialble in Plain Text"""

        return Response(str(self._to_dict()), content_type='text/plain')

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        """Return the APIs avaialble in XMLRPC"""

        params, method = parse_xmlrpc_request(self.request)

        log = logging.getLogger(__name__)
        log.debug('API XMLRPC Request: Method: %s, Params: %s', method, params)

        return xmlrpc_response(self._to_dict())

    def _to_dict(self):
        return APICollection.to_dict()

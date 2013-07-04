from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_xmlrpc import *

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import (
    DBSession,
    Species,
    Occurrence,
    )

from bccvl_visualiser.views import BaseView

import logging

@view_defaults(route_name='api')
class ApiView(BaseView):
    """The API level view"""

    @view_config(renderer='../templates/mytemplate.pt')
    def __call__(self):
        return {'one': 'test', 'project': 'BCCVL_Visualiser'}

    @view_config(name='.json', renderer='json')
    def json(self):
        """Return the APIs avaialble in JSON"""
        log = logging.getLogger(__name__)
        log.debug('HERE IN JSON LAND')
        return self.as_dict()

    @view_config(name='.text')
    def text(self):
        """Return the APIs avaialble in Plain Text"""
        return Response(str(self.as_dict()), content_type='text/plain')

    @view_config(name='.xml')
    def xml(self):
        """Return the APIs avaialble in XML"""
        log = logging.getLogger(__name__)
        params, method = parse_xmlrpc_request(self.request)
        log.debug('HERE IN XML LAND, Params: %s', params)
        return xmlrpc_response(self.as_dict())

    def as_dict(self):
        return { 'content': 'APIS' }

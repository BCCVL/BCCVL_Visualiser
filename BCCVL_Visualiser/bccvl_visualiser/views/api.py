import logging

from pyramid.response import Response
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from sqlalchemy.exc import DBAPIError

from bccvl_visualiser.models import (
    APICollection
    )

from bccvl_visualiser.views import BaseView

@view_defaults(route_name='api')
class ApiCollectionView(BaseView):
    """The API level view"""

    @view_config(renderer='../templates/api_template.pt')
    def __call__(self):
        return self._to_dict()

    @view_config(name='.json', renderer='json')
    def json(self):
        return super(ApiCollectionView, self).json()

    @view_config(name='.text')
    def text(self):
        return super(ApiCollectionView, self).text()

    @view_config(name='.xmlrpc')
    def xmlrpc(self):
        return super(ApiCollectionView, self).xmlrpc()

    def _to_dict(self):
        return APICollection.to_dict()

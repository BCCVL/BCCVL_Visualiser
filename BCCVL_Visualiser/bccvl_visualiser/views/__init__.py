import logging

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.i18n import get_localizer

from zope.interface import Interface, Attribute, implements

from sqlalchemy.exc import DBAPIError

class IView(Interface):

    #: The title of the view. This is displayed in breadcrumbs and page titles.
    Title = Attribute('The title of a view')
    description = Attribute('Description of a view to be displayed')

    def __init__(context, request):
        """Initialisation function for a given view.
        """
        pass

    def __call__():
        """Run view and return a response or something to render to response.
        """
        pass

class BaseView(object):
    """Base Class for all subsequent views"""
    implements(IView)

    Title = None
    description = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.localizer = get_localizer(request)

    def __call__(self):
        values = {
            'localizer': self.localizer
        }

        return values

    def json(self):
        """Return _to_dict as JSON"""

        log = logging.getLogger(__name__)
        log.debug('.json request')

        return self._to_dict()

    def text(self):
        """Return the _to_dict as Plain Text"""

        log = logging.getLogger(__name__)
        log.debug('.text request')

        return Response(str(self._to_dict()), content_type='text/plain')

    def xmlrpc(self):
        """Return _to_dict as an XMLRPC response"""

        params, method = parse_xmlrpc_request(self.request)

        log = logging.getLogger(__name__)
        log.debug('XMLRPC request: Method: %s, Params: %s', method, params)

        return xmlrpc_response(self._to_dict())

    def _to_dict(self):
        """Returns a dictionary version of this view (for JSON, XMLRPC and Text views)"""
        raise NotImplementedError("Please Implement this method")

@view_config(context=Exception)
def error_view(exc, request):
    """ Error view, used to show exceptions."""

    msg = exc.args[0] if exc.args else ""
    response =  Response('Error: %s' % msg)

    log = logging.getLogger(__name__)
    log.error('Error: %s, Params: %s', exc, request.params)

    response.status_int = 500
    return response

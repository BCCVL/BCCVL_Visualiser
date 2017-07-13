import logging
from urlparse import urldefrag

from dogpile.cache import make_region
from pyramid import security
import requests

from bccvl_visualiser.auth import update_auth_cookie


LOG = logging.getLogger(__name__)

# TODO: movke region config to ini file: see region.configure_from_config
region = make_region().configure(
    'dogpile.cache.memory',
    expiration_time=300,  # 5 minutes
)


class Context(object):

    def __init__(self, request):
        self.request = request
        data_url = self.request.params.get('DATA_URL')
        data_url, _ = urldefrag(data_url)
        user_id = security.authenticated_userid(self.request) or security.Everyone

        self.__acl__ = [
            self._get_acls(user_id, data_url.encode('utf-8')),
            security.DENY_ALL
        ]

    @region.cache_on_arguments()
    def _get_acls(self, user_id, data_url):

        # parts = urlsplit(data_url)
        # check_url = urlunsplit((parts.scheme, parts.netloc, parts.path, None, None))
        # # TODO:  ... should we do just a HEAD requset instead of API call?
        # if not check_url.endswith('/'):
        #     check_url = "{0}/".format(check_url)
        # check_url = urljoin(check_url, 'API/site/v1/can_access')

        # TODO: ensure that request Session passes cookie on to correct domain
        s = requests.Session()
        for name in ('__ac',):  # 'serverid'):
            # pass all interesting cookies for our domain on
            # we copy cookies, so that we can set domain etc...
            cookie = self.request.cookies.get(name)
            if not cookie:
                continue
            if name == '__ac':
                # append tokens if we set __ac cookie
                # get my tokens
                tokens = ','.join([token.strip() for token in
                                  self.request.registry.settings.get('authtkt.tokens', '').split('\n') if token.strip()])
                if cookie and tokens:
                    cookie = update_auth_cookie(cookie, tokens, self.request)
            if cookie:
                secure = self.request.registry.get('authtkt.secure', 'False').lower() not in ('false', '0', 'no')
                s.cookies.set(name, cookie, secure=secure, domain=self.request.host, path='/')
        # TODO: use with or whatever to close session
        from pyramid.settings import asbool  # FIXME: avoid circular import?
        verify = asbool(self.request.registry.settings.get('bccvl.ssl.verify', True))
        r = s.head(data_url, verify=verify, allow_redirects=True)
        s.close()
        # TODO: do we have to handle redirects specially?
        if r.status_code == 200:
            permission = security.Allow
        else:
            permission = security.Deny
        # LOG.info('Access %s for user %s to %s', permission, user_id, data_url)
        # LOG.info('   -> %s', r.status_code)
        return (permission, user_id, 'view')

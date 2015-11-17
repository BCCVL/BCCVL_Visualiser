#from urlparse import urljoin, urlsplit, urlunsplit
from urlparse import urldefrag
import requests
from pyramid import security
from dogpile.cache import make_region


# TODO: movke region config to ini file: see region.configure_from_config
region = make_region().configure(
    'dogpile.cache.memory',
    expiration_time=300,  # 5 minutes
)


class Context(object):

    def __init__(self, request):
        self.request = request
        data_url = self.request.params.get('DATA_URL')
        user_id = security.authenticated_userid(self.request) or security.Everyone

        self.__acl__ = [
            self._get_acls(user_id, data_url),
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
        url, _ = urldefrag(data_url)
        s = requests.Session()
        for name in ('__ac',): # 'serverid'):
            # pass all interesting cookies for our domain on
            # we copy cookies, so that we can set domain etc...
            cookie = self.request.cookies.get(name)
            if cookie:
                s.cookies.set(name, cookie, secure=True, domain=self.request.host, path='/')
        # TODO: use with or whatever to close session
        r = s.head(url, verify=False)
        s.close()
        # TODO: do we have to handle redirects specially?
        if r.status_code == 200:
            permission = security.Allow
        else:
            permission = security.Deny
        return (permission, user_id, 'view')

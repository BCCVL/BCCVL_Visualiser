import binascii
import time
from urllib import unquote, quote

from pyramid.authentication import AuthTktAuthenticationPolicy as BasePolicy
from pyramid.authentication import AuthTktCookieHelper as BaseCookieHelper
from pyramid.authentication import VALID_TOKEN
from pyramid.compat import text_type, ascii_native_


class AuthTktAuthenticationPolicy(BasePolicy):

    def __init__(self,
                 secret,
                 callback=None,
                 cookie_name='auth_tkt',
                 secure=False,
                 include_ip=False,
                 timeout=None,
                 reissue_time=None,
                 max_age=None,
                 path="/",
                 http_only=False,
                 wild_domain=False,
                 debug=False,
                 hashalg='md5',
                 ):
        self.cookie = AuthTktCookieHelper(
            secret=secret,
            cookie_name=cookie_name,
            secure=secure,
            include_ip=include_ip,
            timeout=timeout,
            reissue_time=reissue_time,
            max_age=max_age,
            http_only=http_only,
            path=path,
            wild_domain=wild_domain,
            hashalg=hashalg)
        self.callback = callback
        self.debug = debug


class AuthTktCookieHelper(BaseCookieHelper):

    def identify(self, request):
        """ Return a dictionary with authentication information, or ``None``
        if no valid auth_tkt is attached to ``request``"""
        environ = request.environ
        cookie = request.cookies.get(self.cookie_name)

        if cookie is None:
            return None

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'
        ticket = binascii.a2b_base64(unquote(cookie))

        try:
            timestamp, userid, tokens, user_data = self.parse_ticket(
                self.secret, ticket, remote_addr, self.hashalg)
        except self.BadTicket:
            return None

        now = self.now # service tests

        if now is None:
            now = time.time()

        if self.timeout and ( (timestamp + self.timeout) < now ):
            # the auth_tkt data has expired
            return None

        userid_typename = 'userid_type:'
        user_data_info = user_data.split('|')
        for datum in filter(None, user_data_info):
            if datum.startswith(userid_typename):
                userid_type = datum[len(userid_typename):]
                decoder = self.userid_type_decoders.get(userid_type)
                if decoder:
                    userid = decoder(userid)

        reissue = self.reissue_time is not None

        if reissue and not hasattr(request, '_authtkt_reissued'):
            if ( (now - timestamp) > self.reissue_time ):
                # See https://github.com/Pylons/pyramid/issues#issue/108
                tokens = list(filter(None, tokens))
                headers = self.remember(request, userid, max_age=self.max_age,
                                        tokens=tokens)
                def reissue_authtkt(request, response):
                    if not hasattr(request, '_authtkt_reissue_revoked'):
                        for k, v in headers:
                            response.headerlist.append((k, v))
                request.add_response_callback(reissue_authtkt)
                request._authtkt_reissued = True

        environ['REMOTE_USER_TOKENS'] = tokens
        environ['REMOTE_USER_DATA'] = user_data
        environ['AUTH_TYPE'] = 'cookie'

        identity = {}
        identity['timestamp'] = timestamp
        identity['userid'] = userid
        identity['tokens'] = tokens
        identity['userdata'] = user_data
        return identity


    def remember(self, request, userid, max_age=None, tokens=()):
        """ Return a set of Set-Cookie headers; when set into a response,
        these headers will represent a valid authentication ticket.
        ``max_age``
          The max age of the auth_tkt cookie, in seconds.  When this value is
          set, the cookie's ``Max-Age`` and ``Expires`` settings will be set,
          allowing the auth_tkt cookie to last between browser sessions.  If
          this value is ``None``, the ``max_age`` value provided to the
          helper itself will be used as the ``max_age`` value.  Default:
          ``None``.
        ``tokens``
          A sequence of strings that will be placed into the auth_tkt tokens
          field.  Each string in the sequence must be of the Python ``str``
          type and must match the regex ``^[A-Za-z][A-Za-z0-9+_-]*$``.
          Tokens are available in the returned identity when an auth_tkt is
          found in the request and unpacked.  Default: ``()``.
        """

        # WE are only consuming AuthTKT tickets....
        return {}
        # TODO: Also the code belowe generates cookie, which cause a 502 error
        #       if there is a n Apache reverse proxy in front of us

        if max_age is None:
            max_age = self.max_age

        environ = request.environ

        if self.include_ip:
            remote_addr = environ['REMOTE_ADDR']
        else:
            remote_addr = '0.0.0.0'

        user_data = ''

        encoding_data = self.userid_type_encoders.get(type(userid))

        if encoding_data:
            encoding, encoder = encoding_data
            userid = encoder(userid)
            user_data = 'userid_type:%s' % encoding

        new_tokens = []
        for token in tokens:
            if isinstance(token, text_type):
                try:
                    token = ascii_native_(token)
                except UnicodeEncodeError:
                    raise ValueError("Invalid token %r" % (token,))
            if not (isinstance(token, str) and VALID_TOKEN.match(token)):
                raise ValueError("Invalid token %r" % (token,))
            new_tokens.append(token)
        tokens = tuple(new_tokens)

        if hasattr(request, '_authtkt_reissued'):
            request._authtkt_reissue_revoked = True

        ticket = self.AuthTicket(
            self.secret,
            userid,
            remote_addr,
            tokens=tokens,
            user_data=user_data,
            cookie_name=self.cookie_name,
            secure=self.secure,
            hashalg=self.hashalg
            )

        cookie_value = quote(binascii.b2a_base64(ticket.cookie_value()))

        return self._get_cookies(request, cookie_value, max_age)

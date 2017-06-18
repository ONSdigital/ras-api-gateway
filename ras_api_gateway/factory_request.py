##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env
from twisted.web import proxy
from twisted.internet import reactor, ssl
from .factory_client import ProxyClientFactory
from .proxy_tools import ProxyTools
from datetime import datetime, timedelta
from ras_api_gateway.host import router


class ProxyRequest(proxy.ProxyRequest, ProxyTools):
    """ this is where the transaction is initially received """
    protocols = dict(http=ProxyClientFactory, https=ProxyClientFactory)
    noisy = False

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        jwt_token = {
            'expires_at': (datetime.now() + timedelta(seconds=6000)).timestamp(),
            'scope': ['ci:read', 'ci:write']
        }
        self.jwt = ons_env.jwt.encode(jwt_token).encode()

    def process(self):
        """ the is the request processor / main decision maker """
        try:
            headers = self.getAllHeaders().copy()
            self.content.seek(0, 0)
            data = self.content.read()
            route = router.route(self.uri.decode())
            print('~~~~~~ROUTE:', type(route), route)
            if route:
                headers[b'host'] = route.host.encode()
                if not ons_env.is_secure:
                    self.syslog('<Inserting JWT Token>')
                    headers[b'authorization'] = self.jwt

                class_ = self.protocols[route.proto]
                client_factory = class_(self.method, self.uri, self.clientproto, headers, data, self)
                if route.ssl:
                    reactor.connectSSL(route.host, route.port, client_factory, ssl.CertificateOptions())
                else:
                    reactor.connectTCP(route.host, route.port, client_factory)
            else:
                self.syslog('no such API endpoint "{}"'.format(self.uri.decode()))
                self.setResponseCode(500, b'no such API endpoint')
                self.finish()
        except Exception as e:
            self.syslog('Error: {}'.format(str(e)))
            self.setResponseCode(500, b'no such API endpoint')
            self.finish()

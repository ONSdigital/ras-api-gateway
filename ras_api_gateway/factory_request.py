##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy
from twisted.internet import reactor, ssl
from .factory_client import ProxyClientFactory
from .proxy_tools import ProxyTools
from .proxy_router import router
from datetime import datetime, timedelta
from .ons_jwt import my_token
from swagger_server.configuration import ons_env



class ProxyRequest(proxy.ProxyRequest, ProxyTools):
    """ this is where the transaction is initially received """
    protocols = dict(http=ProxyClientFactory, https=ProxyClientFactory)
    noisy = False

    def process(self):
        """ the is the request processor / main decision maker """
        headers = self.getAllHeaders().copy()
        self.content.seek(0, 0)
        data = self.content.read()
        route = router.route(self.uri.decode())
        if route:
            headers[b'host'] = route.host.encode()
            if ons_env.fake_jwt:
                jwt_token = {
                    'expires_at': (datetime.now() + timedelta(seconds=6000)).timestamp(),
                    'scope': ['ci:read', 'ci:write']
                }
                jwt = my_token.encode(jwt_token).encode()
                headers[b'authorization'] = jwt

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


##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy
from twisted.web.server import NOT_DONE_YET
from twisted.internet import reactor, ssl
from logging import ERROR
from .factory_client import ProxyClientFactory
from .proxy_tools import ProxyTools
from .proxy_router import router


class ProxyRequest(proxy.ProxyRequest, ProxyTools):
    """ this is where the transaction is initially received """
    protocols = dict(http=ProxyClientFactory, https=ProxyClientFactory)
    noisy = True

    def process(self):
        """ the is the request processor / main decision maker """
        headers = self.getAllHeaders().copy()
        self.content.seek(0, 0)
        data = self.content.read()
        route = router.route(self.uri.decode())
        if route:
            headers[b'host'] = route.host.encode()
            class_ = self.protocols[route.proto]
            self.syslog("=> {} {} {} {} {}".format(self.method, self.clientproto, route.host, route.port, self.uri))
            client_factory = class_(self.method, self.uri, self.clientproto, headers, data, self)
            if route.ssl:
                reactor.connectSSL(route.host, route.port, client_factory, ssl.CertificateOptions())
            else:
                reactor.connectTCP(route.host, route.port, client_factory)
        else:
            self.syslog('no such API endpoint "{}"'.format(self.uri.decode()))
            self.setResponseCode(500, b'no such API endpoint')
            self.finish()


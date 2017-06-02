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

    def process(self):
        """ the is the request processor / main decision maker """
        headers = self.getAllHeaders().copy()
        self.content.seek(0, 0)
        data = self.content.read()
        route = router.route(self.uri)
        headers[b'host'] = route.host.encode()
        if route:
            class_ = self.protocols[route.proto]
            client_factory = class_(self.method, route.url, self.clientproto, headers, data, self)
            if route.ssl:
                reactor.connectSSL(route.host, route.port, client_factory, ssl.CertificateOptions())
            else:
                reactor.connectTCP(route.host, route.port, client_factory)
        else:
            self.syslog(ERROR, 'no such API endpoint "{}"'.format(self.uri))
            self.setResponseCode(500, b'no such API endpoint')
            self.finish()


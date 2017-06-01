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
from logging import INFO
from .factory_client import ProxyClientFactory
from .proxy_tools import ProxyTools
from .proxy_router import router


class ProxyRequest(proxy.ProxyRequest, ProxyTools):
    """ this is where the transaction is initially received """
    protocols = dict(http=ProxyClientFactory, https=ProxyClientFactory)

    def complete(self, *args, **kwargs):
        print("Args>", args)
        print("KWArgs>", kwargs)

    def process(self):
        """ the is the request processor / main decision maker """
        headers = self.getAllHeaders().copy()
        self.content.seek(0, 0)
        data = self.content.read()
        route = router.route(self.uri)
        print("URI>>", route.url)
        if route:
            class_ = self.protocols[route.proto]
            client_factory = class_(self.method, route.uri, self.clientproto, headers, data, self)
            if route.ssl:
                options = ssl.CertificateOptions(verify=False, acceptableProtocols=[b'http/1.1'])
                reactor.connectSSL(route.host, route.port, client_factory, options)
            else:
                reactor.connectTCP(route.host, route.port, client_factory)
        else:
            self.setResponseCode(500, b'no such API endpoint')
            self.finish()


##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy
from urllib.parse import urlparse, urlunparse
from logging import INFO
from .client_factory import ProxyClientFactory
from .proxy_tools import ProxyTools


class ProxyRequest(proxy.ProxyRequest, ProxyTools):
    """ this is where the transaction is initially received """
    protocols = dict(http=ProxyClientFactory)

    def process(self):
        """ the is the request processor / main decision maker """
        self.syslog(INFO, '* in "process" *')
        factory = self.transport.server.factory
        self.syslog(INFO, '> {}'.format(self.uri))

        #parsed = urlparse(self.uri)
        #rest = urlunparse(('', '') + parsed[2:])
        #class_ = self.protocols['http']
        #headers = self.getAllHeaders().copy()
        #self.content.seek(0, 0)
        #s = self.content.read()
        #if not rest: rest += '/'
        #client_factory = class_(self.method, rest, self.clientproto, headers, s, self)
        #self.syslog(client_factory, INFO)


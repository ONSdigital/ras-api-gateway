##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy, http
from logging import INFO
from .request_factory import ProxyRequest
from .proxy_tools import ProxyTools


class Proxy(proxy.Proxy):
    """ set the request factory """
    requestFactory = ProxyRequest


class ProxyFactory(http.HTTPFactory, ProxyTools):
    protocol = Proxy

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.syslog(INFO, '* initialise ProxyFactory *')

    def startFactory(self):
        self.syslog(INFO, '* start ProxyFactory *')

    def stopFactory(self):
        self.syslog(INFO, '* stop ProxyFactory *')



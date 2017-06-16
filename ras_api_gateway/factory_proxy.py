##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy, http
from logging import INFO
from .factory_request import ProxyRequest
from .proxy_tools import ProxyTools


class Proxy(proxy.Proxy):
    """ set the request factory """
    requestFactory = ProxyRequest
    noisy = False

class ProxyFactory(http.HTTPFactory, ProxyTools):
    protocol = Proxy
    noisy = False


##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy, http
from twisted.python import log
from datetime import datetime
from .factory_request import ProxyRequest
from .proxy_tools import ProxyTools

class Proxy(proxy.Proxy):
    """ set the request factory """
    requestFactory = ProxyRequest
    noisy = False

class ProxyFactory(http.HTTPFactory, ProxyTools):
    protocol = Proxy
    noisy = False

    def log(self, request):
        if request.code != 200:
            log.msg('"{}" - - [{}] "{}" {} {} "-" "-"'.format(
                request.getClientIP(),
                datetime.now(),
                request.uri.decode(),
                request.code,
                request.sentLength
            ))

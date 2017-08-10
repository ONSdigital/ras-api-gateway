"""

   ONS / RAS API Gateway
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

"""
from twisted.web import proxy, http
from twisted.python import log
from datetime import datetime
from .factory_request import ProxyRequest
from ons_ras_common import ons_env

#
#   Over-ride the default proxy logger so we just record non-200 responses
#

class Proxy(proxy.Proxy):
    """ set the request factory """
    requestFactory = ProxyRequest
    noisy = False

class ProxyFactory(http.HTTPFactory):
    protocol = Proxy
    noisy = False

    def log(self, request):
        if request.code != 200:
            ons_env.logger.error('"{}" - - [{}] "{}" {} {} "-" "-"'.format(
                request.getClientIP(),
                datetime.now(),
                request.uri.decode(),
                request.code,
                request.sentLength
            ))

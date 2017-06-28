##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy
from .proxy_tools import ProxyTools
from logging import DEBUG, INFO, WARN
from twisted.internet.error import ConnectionDone
from ons_ras_common import ons_env

#
#   Strictly speaking these routines are not required, however the first will
#   add CORS support for Titchfield services (which currently don't support
#   CORS) and the second spots unintended network errors.
#


class MyProxyClient(proxy.ProxyClient):

    def __init__(self, *args, **kwargs):
        self._cors = False
        super().__init__(*args, **kwargs)

    def handleHeader(self, key, value):
        #print("{} == {}".format(key, value))
        if key.lower() == b'access-control-allow-origin':
            self._cors = True
        super().handleHeader(key, value)

    def handleEndHeaders(self):
        """Insert a CORS header in the return path"""
        if not self._cors:
            #print("** ADDING CORS")
            self.father.responseHeaders.addRawHeader('Access-Control-Allow-Origin', '*')
        #else:
        #    print("** CORS NOT NEEDED")
        super().handleEndHeaders()


class ProxyClientFactory(proxy.ProxyClientFactory, ProxyTools):
    """ intercept connection startup and shutdown """
    protocol = MyProxyClient
    noisy = False

    def clientConnectionLost(self, connector, reason):
        if reason.type != ConnectionDone:
            self.syslog(WARN, '* warning - connection lost "{}"'.format(reason.value))

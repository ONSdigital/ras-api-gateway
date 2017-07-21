"""

   ONS / RAS API Gateway
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

"""
from twisted.web import proxy
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
        if key.lower() == b'access-control-allow-origin':
            self._cors = True
        super().handleHeader(key, value)

    def handleEndHeaders(self):
        """Insert a CORS header in the return path"""
        if not self._cors:
            self.father.responseHeaders.addRawHeader('Access-Control-Allow-Origin', '*')
        super().handleEndHeaders()


class ProxyClientFactory(proxy.ProxyClientFactory):
    """ intercept connection startup and shutdown """
    protocol = MyProxyClient
    noisy = False

    def clientConnectionLost(self, connector, reason):
        if reason.type != ConnectionDone:
            ons_env.logger.warning('warning - connection lost "{}"'.format(reason.value))

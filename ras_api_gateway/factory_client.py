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


class MyProxyClient(proxy.ProxyClient):

    def handleResponseEnd(self):
        self.headers['Access-Control-Allow-Origin'] = '*'
        super().handleResponseEnd()
        #if not self._finished:
        #    self._finished = True
        #    self.father.finish()
        #    self.transport.loseConnection()


class ProxyClientFactory(proxy.ProxyClientFactory, ProxyTools):
    """ intercept connection startup and shutdown """
    protocol = MyProxyClient
    noisy = False

    def clientConnectionLost(self, connector, reason):
        if reason.type != ConnectionDone:
            self.syslog(WARN, '* warning - connection lost "{}"'.format(reason.value))

    def logPrefix(self):
        return "[** proxyclientfactory**]"
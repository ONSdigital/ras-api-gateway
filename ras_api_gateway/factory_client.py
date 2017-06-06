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


class ProxyClientFactory(proxy.ProxyClientFactory, ProxyTools):
    """ intercept connection startup and shutdown """
    protocol = proxy.ProxyClient
    noisy = True

    def startedConnecting(self, connector):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass

    def clientConnectionLost(self, connector, reason):
        if reason.type != ConnectionDone:
            self.syslog(WARN, '* warning - connection lost "{}"'.format(reason.value))

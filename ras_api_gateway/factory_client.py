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

#class ProxyClient(proxy.ProxyClient):
#    """ Only needed so we can overwrite the response handler (end) """
#    def handleResponseEnd(self):
#        """ It someone chopped the link before, don't finish() """
#        if not self._finished:
#            self._finished = True
#            if not self.father._disconnected: self.father.finish()
#            self.transport.loseConnection()


class ProxyClientFactory(proxy.ProxyClientFactory, ProxyTools):
    """ intercept connection startup and shutdown """
    protocol = proxy.ProxyClient
    noisy = False

    def startedConnecting(self, connector):
        pass
        #self.syslog(DEBUG, "Start> {}".format(connector))

    def clientConnectionFailed(self, connector, reason):
        pass
        #self.syslog(DEBUG, "Failed> {} {}".format(connector, reason))

    def clientConnectionLost(self, connector, reason):
        if reason.type != ConnectionDone:
            self.syslog(WARN, '* warning - connection lost "{}"'.format(reason.value))
        print('80 -> {} :: {} -> {} => ({})'.format(
            connector.port,
            connector.host,
            self.rest.decode(),
            self.father.code
        ))

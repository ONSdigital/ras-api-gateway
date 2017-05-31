##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.web import proxy


class ProxyClient(proxy.ProxyClient):
    """ Only needed so we can overwrite the response handler (end) """
    def handleResponseEnd(self):
        """ It someone chopped the link before, don't finish() """
        if not self._finished:
            self._finished = True
            if not self.father._disconnected: self.father.finish()
            self.transport.loseConnection()


class ProxyClientFactory(proxy.ProxyClientFactory):
    """ intercept connection startup and shutdown """
    protocol = ProxyClient

    def startedConnecting(self, connector):
        """ intercept a connection start """
        connector._id = time()
        self.father.transport.server.factory.connection_map[connector._id] = connector

    def clientConnectionLost(self, connector, reason):
        """ intercept a connection stop """
        del self.father.transport.server.factory.connection_map[connector._id]

    def clientConnectionFailed(self, connector, reason):
        """ intercept a connection fail """
        del self.father.transport.server.factory.connection_map[connector._id]


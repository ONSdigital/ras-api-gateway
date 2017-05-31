##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.internet import reactor
from twisted.python import log
from sys import stdout
from .proxy_factory import ProxyFactory

if __name__ == '__main__':
    log.startLogging(stdout)
    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(8080, ProxyFactory())
    reactor.run()


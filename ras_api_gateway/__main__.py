##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from twisted.web import client
from ras_api_gateway.factory_proxy import ProxyFactory
from ras_api_gateway.host import router
from twisted.python import log
from sys import stdout
from os import getenv
#log.startLogging(stdout)
#
#   This is the standard / minimal startup routine with a callback designed
#   to startup an additional Twisted service on port 8080. (the proxy) We're
#   going to call router.activate once after a 1s delay, then router.expire
#   every 8s.
#
if __name__ == '__main__':

    def callback(app):
        client._HTTP11ClientFactory.noisy = False
        reactor.suggestThreadPoolSize(200)
        reactor.listenTCP(int(getenv('PORT', 8080)), ProxyFactory())
        reactor.callLater(1, router.activate)
        #LoopingCall(router.expire).start(8, now=False)

    ons_env.activate(callback)



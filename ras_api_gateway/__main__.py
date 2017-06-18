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

if __name__ == '__main__':

    def callback(app):
        client._HTTP11ClientFactory.noisy = False
        reactor.suggestThreadPoolSize(200)
        reactor.listenTCP(8080, ProxyFactory())
        reactor.callLater(0, router.activate)
        LoopingCall(router.expire).start(8)

    ons_env.activate(callback)

    #logging.getLogger('twisted').setLevel(logging.DEBUG)
    #log.startLogging(stdout)



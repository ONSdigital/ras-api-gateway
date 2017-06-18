##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env
from twisted.internet import reactor
from ras_api_gateway.factory_proxy import ProxyFactory
#from ras_api_gateway.host import router
from ras_api_gateway.host import router

if __name__ == '__main__':

    def callback(app):
        reactor.suggestThreadPoolSize(200)
        reactor.listenTCP(8080, ProxyFactory())
        reactor.callLater(0, router.activate)

    ons_env.activate(callback)

    #logging.getLogger('twisted').setLevel(logging.DEBUG)
    #log.startLogging(stdout)
    #client._HTTP11ClientFactory.noisy = False


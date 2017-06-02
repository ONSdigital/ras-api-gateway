##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.internet import reactor
from twisted.python import log
from flask_twisted import Twisted
from sys import stdout
from ras_api_gateway.factory_proxy import ProxyFactory
from swagger_server.configuration import ons_env
from connexion import App
from flask_cors import CORS
from ras_api_gateway.proxy_router import router


if __name__ == '__main__':
    ons_env.activate()
    log.startLogging(stdout)
    app = App(__name__, specification_dir='../swagger_server/swagger/')
    CORS(app.app)
    app.add_api('swagger.yaml', arguments={'title': 'ONS Microservice'})
    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(8000, ProxyFactory())
    reactor.callLater(1, router.setup)
    Twisted(app).run(port=ons_env.port)


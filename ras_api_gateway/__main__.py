##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from crochet import no_setup
no_setup()

from twisted.internet import reactor
from twisted.python import log
from twisted.web import client
from flask_twisted import Twisted
from sys import stdout
from ras_api_gateway.factory_proxy import ProxyFactory
from swagger_server.configuration import ons_env
from connexion import App
from flask_cors import CORS
from ras_api_gateway.proxy_router import router
import logging

if __name__ == '__main__':
    ons_env.activate()
    logging.getLogger('twisted').setLevel(logging.DEBUG)
    log.startLogging(stdout)
    client._HTTP11ClientFactory.noisy = True
    app = App(__name__, specification_dir='../swagger_server/swagger/')
    CORS(app.app)
    try:
        with open('../swagger_server/swagger/swagger.yaml') as io:
            print("**** FOUND PATH 1")
    except Exception:
        print("#### 1 NOT FOUND")

    try:
        with open('swagger_server/swagger/swagger.yaml') as io:
            print("**** FOUND PATH 2")
    except Exception:
        print("#### 2 NOT FOUND")

    app.add_api('swagger.yaml', arguments={'title': 'ONS Microservice'})
    reactor.suggestThreadPoolSize(30)
    reactor.listenTCP(8080, ProxyFactory())
    reactor.callLater(1, router.setup)
    Twisted(app).run(port=8079)


##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.internet import epollreactor
epollreactor.install()
from twisted.internet import reactor
from twisted.python import log
from twisted.web import client
from sys import stdout
from ras_api_gateway.factory_proxy import ProxyFactory
from swagger_server.configuration import ons_env
from ras_api_gateway.proxy_router import router
import logging
from klein import Klein
from twisted.python import log
from werkzeug.routing import Rule
from swagger_server.controllers_local.proxy_controller import benchmark, survey_todo, register, ping

klein = Klein()

def add_route(app, path, target):
    """
    Add a URL route to the internal routing table for Klein

    :param app: Klein instance
    :param route: URL pattern to route (as per Flask)
    :param target: The function to call when this endpoint is hit
    """
    target.segment_count = 0
    endpoint = target.__name__
    app._url_map.add(Rule(path, endpoint=endpoint)) #, target)) #endpoint=target.__name__))
    app._endpoints[endpoint] = target

def execute_endpoint(self, endpoint, *args, **kwargs):
    """
    Execute the named endpoint with all arguments and possibly a bound
    instance.
    """
    log.msg("args=", args)
    log.msg("kwargs=", kwargs)
    endpoint_f = self._endpoints[endpoint]
    return endpoint_f(self._instance, *args, **kwargs)

if __name__ == '__main__':
    ons_env.activate()
    logging.getLogger('twisted').setLevel(logging.DEBUG)
    log.startLogging(stdout)
    client._HTTP11ClientFactory.noisy = False
    reactor.suggestThreadPoolSize(200)
    reactor.listenTCP(8080, ProxyFactory())
    reactor.callLater(1, router.setup)
    #klein.execute_endpoint = execute_endpoint
    add_route(klein, '/benchmark', benchmark)
    add_route(klein, '/api/1.0.0/ping/<host>/<port>', ping)
    add_route(klein, '/api/1.0.0/register', register)
    add_route(klein, '/surveys/todo/<partyId>', survey_todo)
    klein.run("localhost", 8079)


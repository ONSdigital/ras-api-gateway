##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from flask import jsonify, make_response
from ras_api_gateway.proxy_router import router
from twisted.web.server import NOT_DONE_YET
from json import loads
from jinja2 import Environment, FileSystemLoader
from ..configuration import ons_env
import twisted.internet._sslverify as v
from .aggregation import ONSAggregation
from twisted.python import log

#
#   Disable SSL tail certificate verification
#
v.platformTrust = lambda : None

env = Environment(loader=FileSystemLoader('templates'))
aggregator = ONSAggregation()


def get_secret(*args, **kwargs):
    """Test endpoint"""
    return make_response(jsonify("This is a secret"), 200)


def register(*args, **kwargs):
    """Test endpoint"""
    request = args[1]
#    print("Args>", args)
#    print("KWArgs>", kwargs)
    details = request.content.read().decode('utf-8')
    return router.register(request, details)


def unregister(host):
    """Test endpoint"""
    return make_response(jsonify("unregister"), 200)


def status(*args, **kwargs):
    """Test endpoint"""
    try:
        code, msg = router.status()
        return make_response(jsonify(msg), code)
    except Exception as e:
        print(e)


def mygateway():
    """Display a custom my-gateway screen"""
    proto = ons_env.get('protocol')
    host = ons_env.get('api_gateway')
    port = 443 if proto == 'https' else 8080
    base = '{}://{}:{}'.format(proto, host, port)
    try:
        template = env.get_template('mygateway.html')
        items = []
        for endpoint in router.routing_table:
            route = router.routing_table[endpoint]
            if route.is_ui:
                items.append({
                    'ms': 'Unknown microservice',
                    'url': '{}{}'.format(base, route.uri.decode()),
                    'uri': route.uri.decode(),
                    'host': '{}:{}'.format(route.host, route.port),
                    'last': router.last_seen(route)})

        rendered = template.render({'routes': items})
        return make_response(rendered, 200)
    except Exception as e:
        print("ERROR>", e)
        return "FAIL", 404


def ping(*args, **kwargs):
    ##print("Args>", args)
    #print("KWArgs>", kwargs)
    request = args[1]
    host = kwargs.get('host')
    port = kwargs.get('port')
    return router.ping(request, host, port)
    #code, msg = router.ping(host, port)
    #return make_response(msg, code)

#
#   Ok, this needs to go through a layer that assigns KW args
#
def survey_todo(*args, **kwargs): #id=None, status_filter=None):
    """
    Call the TODO aggregated endpoint.

    :param id: The partyId we're interested in
    :param status_filter: The statuses we're interested in
    :return: A data object suitable for producing "mySurveys"
    """
    request = args[1]
    party_id = kwargs.get('partyId', '')

    if b'status_filter' not in request.args:
        request.setResponseCode(500)
        return 'status_filter parameter is missing'

    try:
        status_filter = loads(request.args[b'status_filter'][0].decode())
    except Exception:
        request.setResponseCode(500)
        return 'unable to parse "status_filter"'

    if type(status_filter) != list:
        request.setResponseCode(500)
        return '"status filter" needs to be a JSON format list of statuses'

    return aggregator.pipeline(None, request, [
        [aggregator.CASES_GET, aggregator.my_survey, {'key': party_id, 'status_filter': status_filter}]
    ])


def benchmark(a,b):
    return "OK"


##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from ons_ras_common import ons_env
from flask import jsonify, make_response
from ras_api_gateway.host import router
from json import loads
from jinja2 import Environment, FileSystemLoader
import twisted.internet._sslverify as v
from .aggregation import ONSAggregation
#
#   Disable SSL tail certificate verification
#
v.platformTrust = lambda : None

env = Environment(loader=FileSystemLoader('templates'))
aggregator = ONSAggregation()


def get_secret(*args, **kwargs):
    """Test endpoint"""
    return make_response(jsonify("This is a secret"), 200)


def register(details):
    """Test endpoint"""
    code, msg = router.register(details)
    return make_response(jsonify(msg), code)


def unregister(host):
    """Test endpoint"""
    return make_response(jsonify("unregister"), 200)


def status(*args, **kwargs):
    """Test endpoint"""
    try:
        proto = ons_env.get('protocol')
        host = ons_env.get('api_gateway')
        port = 443 if proto == 'https' else 8080
        base = '{}://{}:{}'.format(proto, host, port)
        #template = env.get_template('mygateway.html')
        items = []
        for endpoint in router.routing_table:
            route = router.routing_table[endpoint]
            if route.is_ui:
                items.append([
                    'Unknown microservice',
                    '<a href="{}{}">{}</a>'.format(base, route.uri.decode(), route.uri.decode()),
                    '{}:{}'.format(route.host, route.port),
                    route.last_seen,
                    route.status
                ])
        result = {
            'draw': 1,
            'recordsTotal': len(items),
            'recordsFiltered': len(items),
            'data': items
        }
        print(result)
        return make_response(jsonify(result), 200)
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
                    'last': route.last_seen})

        rendered = template.render({'routes': items})
        return make_response(rendered, 200)
    except Exception as e:
        print("ERROR>", e)
        return "FAIL", 404


def ping(host, port):
    code, msg = router.ping(host, port)
    return make_response(msg, code)

from twisted.python import log
from sys import stdout
log.startLogging(stdout)

in_flight = 0

def survey_todo(id=None, status_filter=None):
    """
    Call the TODO aggregated endpoint.

    :param id: The partyId we're interested in
    :param status_filter: The statuses we're interested in
    :return: A data object suitable for producing "mySurveys"
    """
    global in_flight

    in_flight += 1
    log.msg("++ In-flight: ", in_flight)
    response = aggregator.survey_todo(id, loads(status_filter))
    in_flight -= 1
    log.msg("-- In-flight: ", in_flight)
    return response

def benchmark():
    global in_flight

    in_flight += 1
    log.msg("++ In-flight: ", in_flight)
    response = make_response(jsonify("unregister"), 200)
    in_flight -= 1
    log.msg("-- In-flight: ", in_flight)
    return response

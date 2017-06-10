##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from flask import jsonify, make_response
from ras_api_gateway.proxy_router import router
from json import loads
from jinja2 import Environment, FileSystemLoader
from ..configuration import ons_env
import twisted.internet._sslverify as v
from .aggregation import ONSAggregation
from traceback import print_exc
from sys import stdout
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


def ping(host, port):
    code, msg = router.ping(host, port)
    return make_response(msg, code)


def survey_todo(id=None, status_filter=None):
    """
    Generate the TODO data for the mySurveys page. This involves making a number of cross-MS
    API calls and aggregating multiple objects types into a single structure. The process is essentially;

    Get Cases associated with the party;
    for each case;
        get the business
        get the exercise
        get the survey based on the survey id in the exercise record
    And in the background we need to get the respondent, also based on the party id.
    The process uses an ASYNC scatter gather technique to run multiple endpoint calls in parallel. Currently this
    is using 'Crotchet', but this is still a running on top of Flask so the aggregated calling part of this MS
    will block, although the proxy/gateway component is fully async.

    TODO: Need to look a Klein or similar for fully async calling

    :param id: This is the party ID of interest (uuid)
    :return: An aggregated record to be consumed by the mySurveys page
    """
    try:
        return aggregator.survey_todo(id, loads(status_filter))
    except Exception as e:
        print('Unexpected exception: ', e)
        print_exc(limit=20, file=stdout)
        return make_response('unexpected error', 500)


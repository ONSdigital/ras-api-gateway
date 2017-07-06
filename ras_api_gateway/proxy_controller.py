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
#
#   Set up a Jinja2 environment to serve up the "mygateways" page
#
env = Environment(loader=FileSystemLoader('templates'))
#
#   Start an instance of the aggregation class. (all aggregation calls / logic
#   go here)
#
aggregator = ONSAggregation()
#
#   These are our native endpoints
#


def register(details):
    """Register a new endpoint"""
    code, msg = router.register_json(details)
    return make_response(jsonify(msg), code)


def status(*args, **kwargs):
    """Get the router status - used by MyGateways every 5s"""
    try:
        items = router.host_list
        result = {
            'draw': 1,
            'recordsTotal': len(items),
            'recordsFiltered': len(items),
            'data': items
        }
        return make_response(jsonify(result), 200)
    except Exception as e:
        print(e)


def get_routes():
    """Recover a full routing table"""
    return make_response(jsonify(router.route_list), 200)


def mygateway():
    """Display a custom my-gateway screen"""
    template = env.get_template('mygateway.html')
    host = ons_env.get('api_host','(no gateway)')
    protocol = ons_env.get('api_protocol','(no protocol)')
    port = ons_env.get('api_port','(no port)')	

    buttons = [
        {'text': 'Testing (test)', 'icon': 'edit', 'active': '', 'status': 'http://ras-api-gateway-test.apps.devtest.onsclofo.uk'},
        {'text': 'Demonstration (Demo)', 'icon': 'desktop', 'active': '', 'status': 'http://ras-api-gateway-demo.apps.devtest.onsclofo.uk'},
        {'text': 'Integration (Int)', 'icon': 'clone', 'active': '', 'status': 'http://ras-api-gateway-int.apps.devtest.onsclofo.uk'},
    ]
    if host == 'localhost':
        buttons = [{'text': 'Local (development)', 'icon': 'home', 'active': 'class="active"', 'status': 'http://localhost:8080'}] + buttons

    settings = {'api_host': host, 'api_port': port, 'api_protocol': protocol, 'buttons': buttons}
    return make_response(template.render(settings), 200)


def ping(host, port):
    """Handle an incoming ping from a Micro-service"""
    code, msg = router.ping(host, port)
    return make_response(msg, code)


def survey_todo(id=None, status_filter=None):
    """
    Call the TODO aggregated endpoint.

    :param id: The partyId we're interested in
    :param status_filter: The statuses we're interested in
    :return: A data object suitable for producing "mySurveys"
    """
    response = aggregator.survey_todo(id, loads(status_filter))
    return response


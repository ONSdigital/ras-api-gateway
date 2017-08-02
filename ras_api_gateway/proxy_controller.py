"""

   ONS / RAS API Gateway
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

"""
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


def register(details):
    """Register a new endpoint"""
    code, msg = router.register_json(details)
    return make_response(jsonify(msg), code)


def get_routes():
    """Recover a full routing table"""
    return make_response(jsonify(router.route_list), 200)

#
#   These are our native endpoints
#


def survey_todo(id=None, status_filter=None):
    """
    Call the TODO aggregated endpoint.

    :param id: The partyId we're interested in
    :param status_filter: The statuses we're interested in
    :return: A data object suitable for producing "mySurveys"
    """
    try:
        status_filter = loads(status_filter)
    except Exception as e:
        return ons_env.logger.error('invalid filter "{}"'.format(str(e)))

    response = aggregator.survey_todo(id, status_filter)
    return response


def info():
    return make_response(jsonify(ons_env.info))

##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from flask import jsonify, make_response
from ras_api_gateway.proxy_router import router
from twisted.internet import reactor
from twisted.internet.error import ConnectionRefusedError, NoRouteError, UserError
from twisted.web.client import Agent, readBody
from twisted.internet.defer import DeferredList
from crochet import wait_for
from json import loads
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
from ..configuration import ons_env
import arrow
import twisted.internet._sslverify as v
#
#   Disable SSL tail certificate verification
#
v.platformTrust = lambda : None

env = Environment(loader=FileSystemLoader('templates'))

inputDateFormat = 'YYYY-MM-DDThh:mm:ss'
outputDateFormat = 'D MMM YYYY'

CASES_GET = '/collection-exercise-api/1.0.0/cases/partyid'
RESPONDENTS_GET = '/collection-exercise-api/1.0.0/respondents'
SURVEY_GET = '/collection-exercise-api/1.0.0/surveys'
BUSINESS_GET = '/collection-exercise-api/1.0.0/businesses/id'
EXERCISE_GET = '/collection-exercise-api/1.0.0/collection-exercise'


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
    try:
        template = env.get_template('mygateway.html')
        items = []
        for endpoint in router.routing_table:
            route = router.routing_table[endpoint]
            if route.is_ui:
                items.append({
                    'ms': 'Unknown microservice',
                    'url': '{}://{}:{}{}'.format(proto, route.host, route.port, route.uri.decode()),
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


def calculate_case_status(caseEvents):
    status = ''
    for event in caseEvents:
        if event['category'] == 'CASE_UPLOADED':
            status = 'Complete'
            break
    if status == '':
        for event in caseEvents:
            if event['category'] == 'CASE_DOWNLOADED':
                status = 'In progress'
                break
    if status == '':
        status = 'Not started'
    return status


def hit_read(response):
    if response.code != 200:
        raise UserError
    return response


def hit_route(uri, params):
    route = router.route(uri)
    if not route: raise NoRouteError
    url = '{}://{}:{}{}/{}'.format(route.proto, route.host, route.port, uri, params).encode()
    deferred = Agent(reactor).request(b'GET', url, None)
    deferred.addCallback(hit_read).addCallback(readBody)
    return deferred


@wait_for(timeout=10)
def lookup_cases(party_id):
    return hit_route(CASES_GET, party_id)

def survey_todo(id=None):
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
        return survey_todo_process(id)
    except Exception as e:
        print('Unexpected exception: ',e)
        return make_response('unexpected error', 500)


def survey_todo_process(party_id):
    """Query various endpoints and aggregate result"""
    results = {}
    rows = []

    try:
        cases = loads(lookup_cases(party_id).decode())
    except ConnectionRefusedError:
        return make_response('case service is not responding', 500)
    except NoRouteError:
        return make_response('no route to case service', 500)
    except UserError:
        return make_response('no such party id "{}"'.format(party_id), 404)
    except Exception as e:
        print("Error>", e)
        return make_response('unknown error', 500)

    def attach(item, case_id, key):
        results[case_id][key] = loads(item.decode())
        return True, None

    @wait_for(timeout=10)
    def fetch_rows():
        dlist = [hit_route(RESPONDENTS_GET, party_id)]
        for case in cases:
            def attach_exercise(ex, case_id):
                ex = results[case_id]['exercise'] = loads(ex.decode())
                for key in ['periodStart', 'periodEnd', 'scheduledReturn']:
                    ex[key] = ex[key].replace('Z', '')
                    ex[key + 'Formatted'] = arrow.get(ex[key], inputDateFormat).format(outputDateFormat)
                return DeferredList([hit_route(SURVEY_GET, ex['surveyId']).addCallback(attach, case_id, 'survey')])
            case_id = case['id']
            business_id = case['caseGroup']['partyId']
            exercise_id = case['caseGroup']['collectionExerciseId']
            results[case_id] = {'case': case}
            business = hit_route(BUSINESS_GET, business_id).addCallback(attach, case_id, 'business')
            exercise = hit_route(EXERCISE_GET, exercise_id).addCallback(attach_exercise, case_id)
            dlist += [business, exercise]
        return DeferredList(dlist)

    deferreds = fetch_rows()
    for deferred in deferreds:
        if not deferred[0]:
            return deferred[1] if deferred[1] == str else deferred[1].getErrorMessage(), 500
    [rows.append({
        'businessData': item['business'],
        'case': item['case'],
        'collectionExerciseData': item['exercise'],
        'surveyData': item['survey'],
        'status': calculate_case_status(item['case']['caseEvents'])
    }) for item in results.values()]
    return make_response(jsonify({'userData': loads(deferreds[0][1].decode()), 'rows': rows}), 200)

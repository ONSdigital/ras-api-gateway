from flask import request, jsonify, make_response
from ras_api_gateway.proxy_router import router
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import DeferredList
from crochet import wait_for,run_in_reactor
from json import loads
from jinja2 import Environment, FileSystemLoader, Template
import arrow

env = Environment(loader=FileSystemLoader('templates'))

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
        print(code)
        print(msg)
        return make_response(jsonify(msg), code)
    except Exception as e:
        print(e)

def mygateway():
    """Display a custom my-gateway screen"""
    try:
        template = env.get_template('mygateway.html')
        items = []
        for endpoint in router.routing_table:
            route = router.routing_table[endpoint]
            if route.is_ui:
                items.append({'ms': 'Unknown microservice', 'url': route.uri.decode()})

        rendered = template.render({'routes': items})
        return make_response(rendered, 200)
    except Exception as e:
        print("ERROR>", e)
        return "FAIL", 404


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


def survey_todo(id=None):
    """Query various endpoints and aggregate result"""
    if not id:
        return 'no party id was specified', 500
    party_id = id
    inputDateFormat = 'YYYY-MM-DDThh:mm:ss'
    outputDateFormat = 'D MMM YYYY'

    @wait_for(timeout=10)
    def parallel():

        dRespondent = Agent(reactor).request(
            b'GET',
            ('http://localhost:8000/collection-exercise-api/1.0.0/respondents/'+id).encode(),
            None)
        dRespondent.addCallback(readBody)
        dCases = Agent(reactor).request(
            b'GET',
            ('http://localhost:8000/collection-exercise-api/1.0.0/cases/partyid/'+id).encode(),
            None)
        dCases.addCallback(readBody)
        return DeferredList([dCases, dRespondent])

    cases, respondent = parallel()
    if not cases[0]:
        return cases[1].getErrorMessage(), 500
    cases = loads(cases[1].decode())

    if not respondent[0]:
        return respondent[1].getErrorMessage(), 500
    respondent = loads(respondent[1].decode())


    @wait_for(timeout=10)
    def process_rows():
        defs = []
        for case in cases:

            def attach_exercise(survey, exercise):
                return {'survey': loads(survey.decode()), 'exercise': exercise}

            def attach_business(business):
                return {'business': loads(business.decode())}

            def get_survey(exercise):
                exercise = loads(exercise.decode())
                survey_id = exercise['surveyId']
                dSurvey = Agent(reactor).request(
                    b'GET',
                    ('http://localhost:8000/collection-exercise-api/1.0.0/surveys/' + survey_id).encode(),
                    None)
                dSurvey.addCallback(readBody)
                dSurvey.addCallback(attach_exercise, exercise)
                return DeferredList([dSurvey])

            exercise_id = case['caseGroup']['collectionExerciseId']
            dExercise = Agent(reactor).request(
                b'GET',
                ('http://localhost:8000/collection-exercise-api/1.0.0/collection-exercise/' + exercise_id).encode(),
                None)
            dExercise.addCallback(readBody)
            dExercise.addCallback(get_survey)
            defs.append(dExercise)

            business_id = case['caseGroup']['partyId']
            dBusiness = Agent(reactor).request(
                b'GET',
                ('http://localhost:8000/collection-exercise-api/1.0.0/businesses/id/' + business_id).encode(),
                None)
            dBusiness.addCallback(readBody)
            dBusiness.addCallback(attach_business)
            defs.append(dBusiness)

            #defs.append(dSurvey)
            #return DeferredList([dBusiness, dExercise])

            #business, exercise = get_row(case)
            #if not business[0]:
            #    return business[1].getErrorMessage(), 500
            #if not exercise[0]:
            #    return exercise[1].getErrorMessage(), 500

            #business = loads(business[1].decode())
            #exercise = loads(exercise[1].decode())
            #survey = get_survey()[0]
            #if not survey[0]:
            #    return survey[1].getErrorMessage(), 500

            #survey = loads(survey[1].decode())

            #for key in ['periodStart', 'periodEnd', 'scheduledReturn']:
            #    exercise[key] = exercise[key].replace('Z', '')
            #    exercise[key+'Formatted'] = arrow.get(exercise[key], inputDateFormat).format(outputDateFormat)

            #results.append({
            #    'userData': respondent,
            #    'businessData': business,
            #    'case': case,
            #    'collectionExerciseData': exercise,
            #    'surveyData': survey,
            #    'status': calculate_case_status(case['caseEvents'])
            #})

        return DeferredList(defs)

    for row in process_rows():
        #print(">>", len(row), row)
        print("========================")
        for item in row:
            print("*****", item)
    return "OK", 200
#    return jsonify(rows), 200



def xsurvey_todo(id=None):
    """Query various endpoints and aggregate result"""

    if not id:
        party_id = '3b136c4b-7a14-4904-9e01-13364dd7b972'
    else:
        party_id = id

    inputDateFormat = 'YYYY-MM-DDThh:mm:ss'
    outputDateFormat = 'D MMM YYYY'

    #allowedStatuses = ['Not started', 'In progress']

    @wait_for(timeout=10)
    def parallel():

        dRespondent = Agent(reactor).request(
            b'GET',
            ('http://localhost:8000/collection-exercise-api/1.0.0/respondents/'+id).encode(),
            None)
        dRespondent.addCallback(readBody)
        dCases = Agent(reactor).request(
            b'GET',
            ('http://localhost:8000/collection-exercise-api/1.0.0/cases/partyid/'+id).encode(),
            None)
        dCases.addCallback(readBody)
        return DeferredList([dCases, dRespondent])

    cases, respondent = parallel()
    if not cases[0]:
        return cases[1].getErrorMessage(), 500

    if not respondent[0]:
        return respondent[1].getErrorMessage(), 500

    def get_row(case):

        @wait_for(timeout=10)
        def stage1():
            business_id = case['caseGroup']['partyId']
            dBusiness = Agent(reactor).request(
                b'GET',
                ('http://localhost:8000/collection-exercise-api/1.0.0/businesses/id/'+business_id).encode(),
                None)
            dBusiness.addCallback(readBody)
            exercise_id = case['caseGroup']['collectionExerciseId']
            dExercise = Agent(reactor).request(
                b'GET',
                ('http://localhost:8000/collection-exercise-api/1.0.0/collection-exercise/'+exercise_id).encode(),
                None)
            dExercise.addCallback(readBody)
            return DeferredList([dBusiness, dExercise])

        d = stage1()
        return d

    def get_survey():

        @wait_for(timeout=10)
        def stage1():
            survey_id = exercise['surveyId']
            dSurvey = Agent(reactor).request(
                b'GET',
                ('http://localhost:8000/collection-exercise-api/1.0.0/surveys/'+survey_id).encode(),
                None)
            dSurvey.addCallback(readBody)
            return DeferredList([dSurvey])

        d = stage1()
        return d

    respondent = loads(respondent[1].decode())
    results = []
    for case in loads(cases[1].decode()):
        business, exercise = get_row(case)
        if not business[0]:
            return business[1].getErrorMessage(), 500
        if not exercise[0]:
            return exercise[1].getErrorMessage(), 500

        business = loads(business[1].decode())
        exercise = loads(exercise[1].decode())
        survey = get_survey()[0]
        if not survey[0]:
            return survey[1].getErrorMessage(), 500

        survey = loads(survey[1].decode())

        for key in ['periodStart', 'periodEnd', 'scheduledReturn']:
            exercise[key] = exercise[key].replace('Z', '')
            exercise[key+'Formatted'] = arrow.get(exercise[key], inputDateFormat).format(outputDateFormat)

        results.append({
            'userData': respondent,
            'businessData': business,
            'case': case,
            'collectionExerciseData': exercise,
            'surveyData': survey,
            'status': calculate_case_status(case['caseEvents'])
        })

    return jsonify(results), 200

from flask import request, jsonify, make_response
from ras_api_gateway.proxy_router import router
from twisted.internet import reactor
from twisted.web.client import Agent, readBody
from twisted.web.http_headers import Headers
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import DeferredList
from crochet import wait_for,run_in_reactor
from json import loads

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


def aggregate():
    """Make an aggregate call"""
    results = []

    @wait_for(timeout=10)
    def parallel():

        agent = Agent(reactor)
        d1 = agent.request(
            b'GET',
            b'http://localhost:8081/collection-exercise-api/1.0.0/collection-exercises',
            None)
        d1.addCallback(readBody)
        agent = Agent(reactor)
        d2 = agent.request(
            b'GET',
            b'http://localhost:8081/collection-exercise-api/1.0.0/collection-exercises',
            None)
        d2.addCallback(readBody)
        return DeferredList([d1,d2])

    @wait_for(timeout=10)
    def get_exercises():
        agent = Agent(reactor)
        d = agent.request(
            b'GET',
            b'http://localhost:8081/collection-exercise-api/1.0.0/collection-exercises',
            None)
        d.addCallback(readBody)
        return d

    @wait_for(timeout=10)
    def get_details(sid=None):
        agent = Agent(reactor)
        d = agent.request(
            b'GET',
            ('http://localhost:8081/collection-exercise-api/1.0.0/surveys/'+sid).encode(),
            None)
        d.addCallback(readBody)
        return d

    @wait_for(timeout=10)
    def get_surveys(survey_ids):
        ds = []
        for sid in survey_ids:
            if not sid:
                continue
            agent = Agent(reactor)
            d = agent.request(
                b'GET',
                ('http://localhost:8000/collection-exercise-api/1.0.0/surveys/'+sid).encode(),
                None)
            d.addCallback(readBody)
            ds.append(d)

        return DeferredList(ds)

    try:
        ids = []
        surveys = {}
        exercises = get_exercises().decode()
        for survey in get_surveys(exercise.get('surveyID', None) for exercise in loads(exercises)):
            print(survey)
            #survey = loads(survey)
            #surveys[survey['id']] = survey

        print(surveys)
        #exercises = get_exercises().decode()
        #for exercise in loads(exercises):
        #    result = {'id': exercise['id']}
        #    survey = loads(get_details(exercise.get('surveyID', '')).decode())
        #    if 'longName' in survey:
        #        result['name'] = survey['longName']
        #    results.append(result)
        #return make_response(jsonify({'results': results}), 200)
    except Exception as e:
        print("Error: ", e)

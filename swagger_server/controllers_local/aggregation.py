##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from flask import jsonify, make_response
from json import loads
from crochet import wait_for
from twisted.internet import reactor
from twisted.internet.error import ConnectionRefusedError, NoRouteError, UserError
from twisted.web import client
from twisted.web.client import Agent, readBody
from twisted.internet.defer import DeferredList
from ras_api_gateway.proxy_router import router
from functools import wraps
import treq
import arrow
import queue
client._HTTP11ClientFactory.noisy = False

def async_wait():
    def required_decorator(original_function):
        @wraps(original_function)
        def required_wrapper(*args, **kwargs):
            async_queue = queue.Queue()
            dl = original_function(*args, **kwargs)
            dl.addCallback(async_queue.put_nowait)
            return async_queue.get()
        return required_wrapper
    return required_decorator



class ONSAggregation(object):
    """
    This class contains the workings for aggregated calls as defined in the proxy_controller. If it becomes
    too substantial, this may need splitting down further, but for now it's a good place to scrutinise the pattern.
    """
    inputDateFormat = 'YYYY-MM-DDThh:mm:ss'
    outputDateFormat = 'D MMM YYYY'
    CASES_GET = '/collection-exercise-api/1.0.0/cases/partyid'
    RESPONDENTS_GET = '/collection-exercise-api/1.0.0/respondents'
    SURVEY_GET = '/collection-exercise-api/1.0.0/surveys'
    BUSINESS_GET = '/collection-exercise-api/1.0.0/businesses/id'
    EXERCISE_GET = '/collection-exercise-api/1.0.0/collection-exercise'

    def hit_read(self, response):
        if response.code != 200:
            raise UserError
        return response

    def hit_route(self, uri, params):
        route = router.route(uri)
        if not route: raise NoRouteError
        url = '{}://{}:{}{}/{}'.format(route.proto, route.host, route.port, uri, params).encode()
        return treq.get(url).addCallback(self. hit_read).addCallback(treq.content) #readBody)

    @async_wait() #@wait_for(timeout=10)
    def lookup_cases(self, party_id):
        return self.hit_route(self.CASES_GET, party_id)

    def calculate_case_status(self, caseEvents):
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

    def survey_todo(self, party_id, status_filter):
        """Query various endpoints and aggregate result"""
        if type(status_filter) != list:
            return make_response('"status filter" needs to be a JSON format list of statuses', 500)

        results = {}
        rows = []
        try:
            cases = loads(self.lookup_cases(party_id).decode())
        except ConnectionRefusedError:
            return make_response('case service is not responding', 500)
        except NoRouteError:
            return make_response('no route to case service', 500)
        except UserError:
            return make_response('no such party id "{}"'.format(party_id), 404)
        except Exception as e:
            print("Error>", e)
            return make_response('unknown error', 500)

        def attach(blob, case_id, key):
            results[case_id][key] = loads(blob.decode())
            return True, None

        @async_wait() #@wait_for(timeout=10)
        def fetch_rows():
            dlist = [self.hit_route(self.RESPONDENTS_GET, party_id)]
            for case in cases:
                def attach_exercise(ex, case_id):
                    ex = results[case_id]['exercise'] = loads(ex.decode())
                    for key in ['periodStart', 'periodEnd', 'scheduledReturn']:
                        ex[key] = ex[key].replace('Z', '')
                        ex[key + 'Formatted'] = arrow.get(ex[key], self.inputDateFormat).format(self.outputDateFormat)
                    return DeferredList([self.hit_route(self.SURVEY_GET, ex['surveyId']).addCallback(attach, case_id, 'survey')])
                case_id = case['id']
                business_id = case['caseGroup']['partyId']
                exercise_id = case['caseGroup']['collectionExerciseId']
                results[case_id] = {'case': case}
                business = self.hit_route(self.BUSINESS_GET, business_id).addCallback(attach, case_id, 'business')
                exercise = self.hit_route(self.EXERCISE_GET, exercise_id).addCallback(attach_exercise, case_id)
                dlist += [business, exercise]
            return DeferredList(dlist)

        deferreds = fetch_rows()
        for deferred in deferreds:
            if not deferred[0]:
                return deferred[1] if deferred[1] == str else deferred[1].getErrorMessage(), 500
        for item in results.values():
            item_status = self.calculate_case_status(item['case']['caseEvents']).lower()
            if item_status in status_filter:
                rows.append({
                    'businessData': item['business'],
                    'case': item['case'],
                    'collectionExerciseData': item['exercise'],
                    'surveyData': item['survey'],
                    'status': item_status
                })
        return make_response(jsonify({'userData': loads(deferreds[0][1].decode()), 'rows': rows}), 200)

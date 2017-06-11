##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from flask import jsonify, make_response
from json import loads
from twisted.web import client
from twisted.web.server import NOT_DONE_YET
from twisted.internet.error import ConnectionRefusedError, NoRouteError, UserError
from twisted.internet.defer import DeferredList, Deferred
from ras_api_gateway.proxy_router import router
import treq
import arrow
from twisted.python import log
from json import dumps
#from crochet import wait_for, no_setup
#no_setup()
#
#   We don't really want the default logging 'noise' associated with HTTP client requests
#
client._HTTP11ClientFactory.noisy = False


def hit_me(*args, **kwargs):
    print("HIT ME")
    print("Args>", args)
    print("KWArgs>", kwargs)
    return "Bye!"

def hit_route(url, params):
    """
    Excercise a remote endpoint

    :param url: The url of the endpoint to hit
    :param params: The parameters to tack onto the request
    :return: A deferred object
    """
    log.msg("<<< ROUTE >>>>", url)
    #
    # TODO: this routine expects to hit an endpoint using parameters passed in the path
    # TODO: we will need additional routines for parameters passed by (for example) search string
    #
    def status_check(response):
        """
        Check the return status of a request, if we get a 200 we can continue, otherwise raise an
        error, which will stop the pipeline ultimately returning an errored deferred which should
        register when we check the return results, before we assemble the return data object.

        :param response: The incoming response object
        :return: The response object (we're just a link in the pipeline)
        """
        log.msg("<< WE GOT HERE>>")
        if response.code != 200:
            raise UserError
        return response

    route = router.route(url)
    if not route:
        raise NoRouteError
    path = '{}/{}'.format(route.txt, params)
    log.msg("Calling: ", path)
    return treq.get(path).addCallback(status_check).addCallback(treq.content)


class ONSAggregation(object):
    """
    Provide an library of aggregation functions that will obtain data from other micro-services
    and provide the client with an aggregated result.
    """
    # TODO: refactor into config file
    inputDateFormat = 'YYYY-MM-DDThh:mm:ss'
    outputDateFormat = 'D MMM YYYY'
    CASES_GET = '/collection-exercise-api/1.0.0/cases/partyid'
    RESPONDENTS_GET = '/collection-exercise-api/1.0.0/respondents'
    SURVEY_GET = '/collection-exercise-api/1.0.0/surveys'
    BUSINESS_GET = '/collection-exercise-api/1.0.0/businesses/id'
    EXERCISE_GET = '/collection-exercise-api/1.0.0/collection-exercise'

    @staticmethod
    def calculate_case_status(case_events):
        """
        Business logic to determine the status of an event

        :param case_events: A list of case events
        :return: A status string in ['Not Started', 'Completed', 'In Progress']
        """
        status = ''
        for event in case_events:
            if event['category'] == 'CASE_UPLOADED':
                status = 'Complete'
                break
        if status == '':
            for event in case_events:
                if event['category'] == 'CASE_DOWNLOADED':
                    status = 'In progress'
                    break
        if status == '':
            status = 'Not started'
        return status

    def fix_dates(self, ex):
        for key in ['periodStart', 'periodEnd', 'scheduledReturn']:
            ex[key] = ex[key].replace('Z', '')
            ex[key + 'Formatted'] = arrow.get(ex[key], self.inputDateFormat).format(self.outputDateFormat)

    @staticmethod
    def access(request, endpoint, chain, params):

        def check_result(response):
            if type(response) == str:
                request.setResponseCode(500)
                return response
            request.setResponseCode(response.code)
            if response.code != 200:
                return str(response)

            if chain:
                return treq.content(response).addCallback(chain, request, params)
            else:
                return treq.content(response)

        route = router.route(endpoint)
        if not route:
            request.setResponseCode(500)
            return 'no route to host'
        return treq.get('{}/{}'.format(route.txt, params['key'])).addCallback(check_result)

    def access2(self, *args, **kwargs):
        #request, pipeline):

        print("Args>", args)
        print("KW>", kwargs)

        request = args[0]
        pipeline = args[1]

        log.msg("----Request>", request)
        log.msg("----Pipelin>", pipeline)

        head, *tail = pipeline
        endpoint, chain, params = head

        log.msg("Endpoint>", endpoint)
        log.msg("Chain>", chain)
        log.msg("Params>", params)

        def check_result(response):
            if type(response) == str:
                request.setResponseCode(500)
                return response
            request.setResponseCode(response.code)
            if response.code != 200:
                return str(response)

            deferred = treq.content(response)
            if chain:
                deferred.addCallback(chain, request, params)
                if len(tail):
                    log.msg("****************************")
                    log.msg(">>", tail)
                    deferred.addCallback(self.access2, request, tail)
            return deferred

        route = router.route(endpoint)
        if not route:
            request.setResponseCode(500)
            return 'no route to host'

        log.msg("*******")
        log.msg("Params>", params)
        log.msg("*******")

        return treq.get('{}/{}'.format(route.txt, params['key'])).addCallback(check_result)


    def my_survey(self, cases, request, params):

        results = {}
        cases = loads(cases.decode())

        def pipe(data, request, params):
            log.msg("PACKET_______________>", params)
            pkt = results[params['case_id']][params['tag']] = loads(data.decode())
            if 'ref' in params:
                params['key'] = pkt[params['ref']]
                log.msg('** Setting "{}" to "{}"'.format(params['ref'], params['key']))
            return True, None

        #def next2(blob, request, params):
        #    results[params['case_id']][params['tag']] = loads(blob.decode())
        #    self.fix_dates(results[params['case_id']][params['tag']])
        #    return self.access(request, self.SURVEY_GET, next1, {'case_id': params['case_id'], 'key': ex['surveyId'], 'tag': 'surveyData'})

        dlist = [self.access(request, self.RESPONDENTS_GET, None, params)]
        for case in cases:

            case_id = case['id']
            business_id = case['caseGroup']['partyId']
            exercise_id = case['caseGroup']['collectionExerciseId']
            results[case_id] = {'case': case}
            results[case_id]['status'] = self.calculate_case_status(case['caseEvents']).lower()
            #business = self.access(request, self.BUSINESS_GET, next1, {'case_id': case_id, 'key': business_id, 'tag': 'businessData'})
            #exercise = self.access(request, self.EXERCISE_GET, next2, {'case_id': case_id, 'key': exercise_id, 'tag': 'collectionExerciseData'})

            exercise = self.access2(request, [
                [self.EXERCISE_GET, pipe, {'case_id': case_id, 'key': exercise_id, 'tag': 'collectionExerciseData'}],
                [self.SURVEY_GET,   pipe, {'case_id': case_id, 'ref': 'surveyId',  'tag': 'surveyData', 'code': self.fix_dates}]
            ])
            dlist += [exercise]
            #dlist += [business, exercise]

        log.msg(dlist)

        def done(deferreds):
            for deferred in deferreds:
                log.msg("Def>", deferred)
                if not deferred[0]:
                    request.setResponseCode(500)
                    return deferred[1] if deferred[1] == str else deferred[1].getErrorMessage()

            return dumps({'userData': loads(deferreds[0][1].decode()), 'rows': list(results.values())})

        return DeferredList(dlist).addCallback(done)



    #============================================================================================================


    #@inlineCallbacks
    #def lookup_cases(self, party_id):
    #    """
    #    Excercise an endpoint making sure we call it in the Twisted reactor (and block for a result)

    #    :param party_id: The partyId to search for
    #    :return: A Case record
    #    """
    #    result = yield hit_route(self.CASES_GET, party_id)
    #    return result

    def survey_todo(self, request, party_id, status_filter):
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

        :param id: This is the party ID of interest (uuid)
        :param status_filter: An array of requested statuses (string)
        :return: An aggregated record to be consumed by the mySurveys page
        """
        if type(status_filter) != list:
            return make_response('"status filter" needs to be a JSON format list of statuses', 500)
        #
        #   This is the first call-out, we're looking to recover the case records for a given party. We
        #   are expecting a response object back (the wait_for in lookup_cases will make it block) so there's
        #   an opportunity to examine errors with a reasonable degree of granularity.
        #
        #   TODO: add logging for error cases
        #
        try:
            #result = self.lookup_cases(party_id)
            log.msg("Result=", "???")
            #cases = loads(result.decode())

            def scatter(result):
                log.msg(">>", result)
                #request.write("<OK>")
                #request.finish()
                return

            deferred = hit_route(self.CASES_GET, party_id)
            deferred.addCallback(scatter)
            return NOT_DONE_YET
        except ConnectionRefusedError:
            return make_response('case service is not responding', 500)
        except NoRouteError:
            return make_response('no route to case service', 500)
        except UserError:
            request.setResponseCode(404)
            return 'no such party id "{}"'.format(party_id)
            return make_response('no such party id "{}"'.format(party_id), 404)
        except Exception as e:
            request.setResponseCode(500)
            return str(e)
            return make_response(str(e), 500)

        def attach(blob, case_id, key):
            """
            This is a convenience method that is executed when a request to another micro-service completes. It
            will essentially decode the result (convert from byte to string) then reformat from a string into
            a dict item with JSON.loads. So once we have Python formatted data, we're going to write it back
            into the results object - which is consumed at the end of the routine by the loop that constructs
            the object we're going to return to the requester.

            :param blob: The response data from the other microservice
            :param case_id: The case_id we're going to associate the response with
            :param key: The particular response we're expecting, i.e. business, survey, etc ...
            :return: A tuple emulating a successfully completed deferred() request
            """
            results[case_id][key] = loads(blob.decode())
            return True, None
        #
        #   results is the object we use to store results as they come back from the various remote requests
        #
        results = {}

        #@wait_for(timeout=5)
        #@inlineCallbacks
        def fetch_rows():
            """
            This is the fan-out routine which will generate endpoint requests. Each request has an associated
            deferred result (often called a 'promise') which is added to 'dlist'. We initially populate dlist
            with a request to look up the respondent by partyId, this will be executed in parallel with all
            ther other requests we're making.

            :return: A list of (completed) deferred objects
            """
            dlist = [hit_route(self.RESPONDENTS_GET, party_id)]
            for case in cases:
                def attach_exercise(ex, case_identifier):
                    ex = results[case_identifier]['exercise'] = loads(ex.decode())
                    for key in ['periodStart', 'periodEnd', 'scheduledReturn']:
                        ex[key] = ex[key].replace('Z', '')
                        ex[key + 'Formatted'] = arrow.get(ex[key], self.inputDateFormat).format(self.outputDateFormat)
                    return DeferredList([hit_route(self.SURVEY_GET, ex['surveyId']).addCallback(attach, case_identifier, 'survey')])
                case_id = case['id']
                business_id = case['caseGroup']['partyId']
                exercise_id = case['caseGroup']['collectionExerciseId']
                results[case_id] = {'case': case}
                business = hit_route(self.BUSINESS_GET, business_id).addCallback(attach, case_id, 'business')
                exercise = hit_route(self.EXERCISE_GET, exercise_id).addCallback(attach_exercise, case_id)
                dlist += [business, exercise]
            return DeferredList(dlist)

        deferreds = [] #yield fetch_rows()
        #
        #   We arrive back here when all the deferred requests in fetch_rows have completed. (thanks to the
        #   'wait_for' decorator on fetch_rows. At this point each deferred is a tuple of (True|False) and
        #   the response object. A quick check of the first item of each deferred will let us spot any
        #   errors. If the result has come back as a string, return (msg, 500), otherwise if we have
        #   a proper response object, try to extract the error message from it. Either way, if any of
        #   the requests failed, we're going to fail here with a 500.
        #
        for deferred in deferreds:
            if not deferred[0]:
                return deferred[1] if deferred[1] == str else deferred[1].getErrorMessage(), 500
        #
        #   This is the 'gather' stage, it might seem a little counter-intuitive looking a the above test,
        #   but the returning deferreds contain resulting status information and meta-data. As requests have
        #   completed, they've been calling 'attach' which has been inserting the data we're interested in
        #   into the 'results' object. So at this point, we're going to cycle through the results object
        #   and build up slightly reformatted objects into a list to return to the user.
        #
        #   TODO: if (!) we were to standardise on attribute names, we could essentially add a status
        #   TODO: item to each object, then just return list(results.values()) rather than 'rows'
        #   TODO: i.e. you could remove the iteration and need for 'rows'
        #
        rows = []
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
        request.write(jsonify({'userData': loads(deferreds[0][1].decode()), 'rows': rows}))
        request.finish()
#        return make_response(jsonify({'userData': loads(deferreds[0][1].decode()), 'rows': rows}), 200)

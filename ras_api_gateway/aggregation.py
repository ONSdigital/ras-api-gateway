"""

   ONS / RAS API Gateway
   License: MIT
   Copyright (c) 2017 Crown Copyright (Office for National Statistics)

"""
from flask import jsonify, make_response
from json import loads, dumps
from ons_ras_common import ons_env
from twisted.web import client
from twisted.internet.error import ConnectionRefusedError, NoRouteError, UserError
from twisted.internet.defer import DeferredList
from ras_api_gateway.host import router
from urllib.parse import quote
import treq
import arrow
from crochet import wait_for
#
#   We don't really want the default logging 'noise' associated with HTTP client requests
#
client._HTTP11ClientFactory.noisy = False


def hit_route(url, params):
    """
    Excercise a remote endpoint

    :param url: The url of the endpoint to hit
    :param params: The parameters to tack onto the request
    :return: A deferred object
    """
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

        if response.code != 200:
            ons_env.logger.info('ERROR ON "{}"'.format(full_url))
            raise UserError
        return response

    route = router.route(url)
    if not route:
        ons_env.logger.error('no route to host for "{}{}"'.format(url, params))
        raise NoRouteError(url, params)

    if params[0] != '?':
        params = '/'+params

    full_url = '{}{}{}'.format(route.txt, url, params)
    ons_env.logger.info('access "{}"'.format(full_url))
    return treq.get(full_url).addCallback(status_check).addCallback(treq.content)


class ONSAggregation(object):
    """
    Provide an library of aggregation functions that will obtain data from other micro-services
    and provide the client with an aggregated result.
    """
    # TODO: refactor into config file
    inputDateFormat = 'YYYY-MM-DDThh:mm:ss'
    outputDateFormat = 'D MMM YYYY'

    CASES_GET = '/cases/partyid'
    SURVEY_GET = '/surveys'

    RESPONDENTS_GET = '/party-api/v1/respondents/id'
    BUSINESS_GET = '/party-api/v1/businesses/id'

    EXERCISE_GET = '/collectionexercises'
    INSTRUMENT_GET = '/collection-instrument-api/1.0.2/collectioninstrument'

    @staticmethod
    def calculate_case_status(case_events):
        """
        Business logic to determine the status of an event

        :param case_events: A list of case events
        :return: A status string in ['Not Started', 'Completed', 'In Progress']
        """
        status = None
        if case_events:
            for event in case_events:
                if event['category'] == 'SUCCESSFUL_RESPONSE_UPLOAD':
                    status = 'Complete'
                    break
                if event['category'] == 'COLLECTION_INSTRUMENT_DOWNLOADED':
                    status = 'Downloaded'
                    break
        return status if status else 'Not Started'

    @wait_for(timeout=5)
    def lookup_cases(self, party_id):
        """
        Excercise an endpoint making sure we call it in the Twisted reactor (and block for a result)

        :param party_id: The partyId to search for
        :return: A Case record
        """
        return hit_route(self.CASES_GET, '{}?{}'.format(party_id,'caseevents=true'))

    def survey_todo(self, party_id, status_filter):
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

        ons_env.logger.debug('survey todo request for "{}"'.format(party_id))

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
            cases = loads(self.lookup_cases(party_id).decode())
        except ConnectionRefusedError:
            return make_response('case service is not responding', 500)
        except NoRouteError:
            return make_response('no route to case service', 500)
        except UserError:
            return make_response('no such party id "{}"'.format(party_id), 404)
        except Exception as e:
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
            data = loads(blob.decode())
            ons_env.logger.debug('cascade results, case="{}" key="{}"'.format(case_id, key))
            ons_env.logger.debug(data)

            results[case_id][key] = data
            return True, None
        #
        #   results is the object we use to store results as they come back from the various remote requests
        #
        results = {}

        @wait_for(timeout=5)
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
                    if not ex:
                        ons_env.logger.critical('unable to locate exercise')
                        ons_env.logger.critical(results)
                        raise Exception('missing exercise')
                    for key in ['periodStartDateTime', 'periodEndDateTime', 'scheduledReturnDateTime']:
                        if not key in ex:
                            ons_env.logger.critical('missing key "{}" in exercise record with is "{}"'.format(
                                key,
                                ex.get('id', 'no key')
                            ))
                            continue
                        if ex[key]:
                            ex[key] = ex[key].replace('Z', '')
                            ex[key + 'Formatted'] = arrow.get(ex[key], self.inputDateFormat).format(self.outputDateFormat)
                        else:
                            ex[key + 'Formatted'] = 'None'
                    return DeferredList([hit_route(self.SURVEY_GET, ex['surveyId']).addCallback(attach, case_identifier, 'survey')])

                case_id = case['id']
                business_id = case['caseGroup']['partyId']
                exercise_id = case['caseGroup']['collectionExerciseId']
                results[case_id] = {'case': case}
                business = hit_route(self.BUSINESS_GET, business_id).addCallback(attach, case_id, 'business')
                exercise = hit_route(self.EXERCISE_GET, exercise_id).addCallback(attach_exercise, case_id)
                dlist += [business, exercise]
            return DeferredList(dlist)

        try:
            deferreds = fetch_rows()
        except Exception as e:
            return make_response(str(e), 500)

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
                ons_env.logger.error('request failed')
                result = deferred[1] if deferred[1] == str else deferred[1].getErrorMessage()
                ons_env.logger.error(result)
                return make_response(result, 500)
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
            item_status = self.calculate_case_status(item.get('case', {}).get('caseEvents', '')).lower()
            if item_status not in status_filter:
                continue
            rows.append({
                'businessData': item.get('business', '*** NO BUSINESS DATA ***'),
                'case': item.get('case', '*** NO CASE DATA ***'),
                'collectionExerciseData': item.get('exercise', '*** NO EXERCISE DATA ***'),
                'surveyData': item.get('survey', '*** NO SURVEY DATA ***'),
                'status': item_status
            })
        return make_response(jsonify({'userData': loads(deferreds[0][1].decode()), 'rows': rows}), 200)

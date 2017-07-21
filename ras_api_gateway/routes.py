"""

    ONS Static Routing table
    License: MIT
    Copyright (c) 2017 Crown Copyright (Office for National Statistics)

"""
import os

RM_CASE_SERVICE_HOST = os.getenv('RM_CASE_SERVICE_HOST', 'localhost')
RM_CASE_SERVICE_PORT = os.getenv('RM_CASE_SERVICE_PORT', 8171)
RM_CASE_SERVICE_PROTOCOL = os.getenv('RM_CASE_SERVICE_PROTOCOL', 'http')

RM_CE_SERVICE_HOST = os.getenv('RM_COLLECTIONEXERCISE_SERVICE_HOST', 'localhost')
RM_CE_SERVICE_PORT = os.getenv('RM_COLLECTIONEXERCISE_SERVICE_PORT', 5300)
RM_CE_SERVICE_PROTOCOL = os.getenv('RM_COLLECTIONEXERCISE_SERVICE_PROTOCOL', 'http')

RM_IAC_SERVICE_HOST = os.getenv('RM_IAC_SERVICE_HOST', 'localhost')
RM_IAC_SERVICE_PORT = os.getenv('RM_IAC_SERVICE_PORT', 5201)
RM_IAC_SERVICE_PROTOCOL = os.getenv('RM_IAC_SERVICE_PROTOCOL', 'http')

RM_SURVEY_SERVICE_HOST = os.getenv('RM_SURVEY_SURVEY_HOST', 'localhost')
RM_SURVEY_SERVICE_PORT = os.getenv('RM_SURVEY_SURVEY_PORT', 5301)
RM_SURVEY_SERVICE_PROTOCOL = os.getenv('RM_SURVEY_SURVEY_PROTOCOL', 'http')

RM_NOTIFY_GATEWAY_SERVICE_HOST = os.getenv('RM_NOTIFY_GATEWAY_SERVICE_HOST', 'localhost')
RM_NOTIFY_GATEWAY_SERVICE_PORT = os.getenv('RM_NOTIFY_GATEWAY_SERVICE_PORT', 5302)
RM_NOTIFY_GATEWAY_SERVICE_PROTOCOL = os.getenv('RM_NOTIFY_GATEWAY_SERVICE_PROTOCOL', 'http')

RM_ACTION_SERVICE_HOST = os.getenv('RM_ACTION_SERVICE_HOST', 'localhost')
RM_ACTION_SERVICE_PORT = os.getenv('RM_ACTION_SERVICE_PORT', 5303)
RM_ACTION_SERVICE_PROTOCOL = os.getenv('RM_ACTION_SERVICE_PROTOCOL', 'http')

RM_SAMPLE_SERVICE_HOST = os.getenv('RM_SAMPLE_SERVICE_HOST', 'localhost')
RM_SAMPLE_SERVICE_PORT = os.getenv('RM_SAMPLE_SERVICE_PORT', 5304)
RM_SAMPLE_SERVICE_PROTOCOL = os.getenv('RM_SAMPLE_SERVICE_PROTOCOL', 'http')

RAS_PARTY_SERVICE_HOST = os.getenv('RAS_PARTY_SERVICE_HOST', 'localhost')
RAS_PARTY_SERVICE_PORT = os.getenv('RAS_PARTY_SERVICE_PORT', 5201)
RAS_PARTY_SERVICE_PROTOCOL = os.getenv('RAS_PARTY_SERVICE_PROTOCOL', 'http')

RAS_CI_SERVICE_HOST = os.getenv('RAS_COLLECTION_INSTRUMENT_SERVICE_HOST', 'localhost')
RAS_CI_SERVICE_PORT = os.getenv('RAS_COLLECTION_INSTRUMENT_SERVICE_PORT', 5305)
RAS_CI_SERVICE_PROTOCOL = os.getenv('RAS_COLLECTION_INSTRUMENT_SERVICE_PROTOCOL', 'http')

RAS_SECURE_MESSAGING_SERVICE_HOST = os.getenv('RAS_SECURE_MESSAGING_SERVICE_HOST', 'localhost')
RAS_SECURE_MESSAGING_SERVICE_PORT = os.getenv('RAS_SECURE_MESSAGING_SERVICE_PORT', 5306)
RAS_SECURE_MESSAGING_SERVICE_PROTOCOL = os.getenv('RAS_SECURE_MESSAGING_SERVICE_PROTOCOL', 'http')


# FIXME: there is a namespace conflict on /info between the sample service and the action service.


routes = []

routes.append({
    'uri': '/casegroups',
    'host': RM_CASE_SERVICE_HOST,
    'port': RM_CASE_SERVICE_PORT,
    'protocol': RM_CASE_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/cases',
    'host': RM_CASE_SERVICE_HOST,
    'port': RM_CASE_SERVICE_PORT,
    'protocol': RM_CASE_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/categories',
    'host': RM_CASE_SERVICE_HOST,
    'port': RM_CASE_SERVICE_PORT,
    'protocol': RM_CASE_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/collectionexercises',
    'host': RM_CE_SERVICE_HOST,
    'port': RM_CE_SERVICE_PORT,
    'protocol': RM_CE_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/iacs',
    'host': RM_IAC_SERVICE_HOST,
    'port': RM_IAC_SERVICE_PORT,
    'protocol': RM_IAC_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/collection-instrument-api/1.0.2',
    'host': RAS_CI_SERVICE_HOST,
    'port': RAS_CI_SERVICE_PORT,
    'protocol': RAS_CI_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/party-api/v1',
    'host': RAS_PARTY_SERVICE_HOST,
    'port': RAS_PARTY_SERVICE_PORT,
    'protocol': RAS_PARTY_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/archive',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/archives',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/draft',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/drafts',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/message',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/messages',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/thread',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/threads',
    'host': RAS_SECURE_MESSAGING_SERVICE_HOST,
    'port': RAS_SECURE_MESSAGING_SERVICE_PORT,
    'protocol': RAS_SECURE_MESSAGING_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/surveys',
    'host': RM_SURVEY_SERVICE_HOST,
    'port': RM_SURVEY_SERVICE_PORT,
    'protocol': RM_SURVEY_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/texts',
    'host': RM_NOTIFY_GATEWAY_SERVICE_HOST,
    'port': RM_NOTIFY_GATEWAY_SERVICE_PORT,
    'protocol': RM_NOTIFY_GATEWAY_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/emails',
    'host': RM_NOTIFY_GATEWAY_SERVICE_HOST,
    'port': RM_NOTIFY_GATEWAY_SERVICE_PORT,
    'protocol': RM_NOTIFY_GATEWAY_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/notifications',
    'host': RM_NOTIFY_GATEWAY_SERVICE_HOST,
    'port': RM_NOTIFY_GATEWAY_SERVICE_PORT,
    'protocol': RM_NOTIFY_GATEWAY_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/info',
    'host': RM_ACTION_SERVICE_HOST,
    'port': RM_ACTION_SERVICE_PORT,
    'protocol': RM_ACTION_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/actions',
    'host': RM_ACTION_SERVICE_HOST,
    'port': RM_ACTION_SERVICE_PORT,
    'protocol': RM_ACTION_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/actionplans',
    'host': RM_ACTION_SERVICE_HOST,
    'port': RM_ACTION_SERVICE_PORT,
    'protocol': RM_ACTION_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/info2',
    'host': RM_SAMPLE_SERVICE_HOST,
    'port': RM_SAMPLE_SERVICE_PORT,
    'protocol': RM_SAMPLE_SERVICE_PROTOCOL
})
routes.append({
    'uri': '/sampleunitrequests',
    'host': RM_SAMPLE_SERVICE_HOST,
    'port': RM_SAMPLE_SERVICE_PORT,
    'protocol': RM_SAMPLE_SERVICE_PROTOCOL
})

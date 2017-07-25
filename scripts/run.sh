#!/bin/bash
if ! [ -a .build ] ; then
	echo "Creating Virtual Environment"
	virtualenv .build -p python3
fi
source .build/bin/activate
pip3 install -r requirements.txt 
RM_CASE_SERVICE_PORT=80 RM_CASE_SERVICE_HOST=casesvc-int.apps.devtest.onsclofo.uk \
RM_COLLECTIONEXERCISE_SERVICE_PORT=80 RM_COLLECTIONEXERCISE_SERVICE_HOST=collectionexercisesvc-int.apps.devtest.onsclofo.uk \
RM_IAC_SERVICE_PORT=80 RM_IAC_SERVICE_HOST=iacsvc-int.apps.devtest.onsclofo.uk \
RM_SURVEY_SURVEY_PORT=80 RM_SURVEY_SURVEY_HOST=surveysvc-int.apps.devtest.onsclofo.uk \
RM_NOTIFY_GATEWAY_SERVICE_PORT=80 RM_NOTIFY_GATEWAY_SERVICE_HOST=notifygatewaysvc-int.apps.devtest.onsclofo.uk \
RM_ACTION_SERVICE_PORT=80 RM_ACTION_SERVICE_HOST=actionsvc-int.apps.devtest.onsclofo.uk \
RM_SAMPLE_SERVICE_PORT=80 RM_SAMPLE_SERVICE_HOST=samplesvc-int.apps.devtest.onsclofo.uk \
RAS_SECURE_MESSAGING_SERVICE_PORT=80 RAS_SECURE_MESSAGING_SERVICE_HOST=ras-secure-messaging-int.apps.devtest.onsclofo.uk \
RAS_PARTY_SERVICE_PORT=8001 RAS_PARTY_SERVICE_HOST=localhost \
RAS_COLLECTION_INSTRUMENT_SERVICE_PORT=8002 RAS_COLLECTION_INSTRUMENT_SERVICE_HOST=localhost \
python3 -m ras_api_gateway

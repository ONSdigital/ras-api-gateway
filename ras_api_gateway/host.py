##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from datetime import datetime
from json import loads, dumps, decoder
from ons_ras_common import ons_env


class Router(object):

    def __init__(self):
        self._hosts = {}
        self._endpoints = {}

    def info(self, text):
        ons_env.logger.info('[router] {}'.format(text))

    def activate(self):
        self.info('Router is running')
        self.register({
            'protocol': 'http',
            'host': 'localhost',
            'port': ons_env.port,
            'uri': '/api/1.0.0/register'
        })
        self.register({
            'protocol': 'http',
            'host': 'localhost',
            'port': ons_env.port,
            'uri': '/api/1.0.0/ping'
        })
        self._hosts = {}
        print("Hosts:", self._hosts)
        print("Endpoints:", self._endpoints)

    def route(self, uri):
        self.info('Attempt to route {}'.format(uri))
        parts = uri.split('?')[0].split('/')
        while len(parts):
            test = '/'.join(parts)

            print("test:", test, type(test), "endpoints:", self._endpoints)


            if test in self._endpoints:
                print("F1:", test)
                print(">>", self._endpoints[test])
                return self._endpoints[test]
            if test+'/' in self._endpoints:
                print("F2:", test+'/')
                return self._endpoints[test + '/']
            parts.pop()

        print("NO MATCH")
        return None

    def ping(self, host, port):
        key = '{}:{}'.format(host, port)
        if key in self._hosts:
            return 200, 'OK'
        return 204, 'not registered'

        #for route in self.routing_table.values():
        #    print("@@@@@@@@@@",host,port, route.is_ui, route.txt)
        #    if route.port == port and route.host == host and route.is_ui:
        #        route.ping()
        #        return 200, 'OK'

        #return 204, 'not registered'

    def register(self, details):
        """
        Register an endpoint

        :param details: Details of the endpoint (dict)
        """
        for attribute in ['protocol', 'host', 'port', 'uri']:
            if attribute not in details:
                self.info("attribute '{}' is missing".format(attribute))
                return False

        self.update(details)

    def update(self, details):
        """
        Add a new endpoint

        :param details: Endpoint details
        :return: Boolean
        """
        key = '{host}:{port}'.format(**details)
        if key not in self._hosts:
            self._hosts[key] = {'registered': datetime.now()}

        route = Route(details, key)
        self._endpoints[route.path] = route
        self.info('registered "{uri}"'.format(**details))

    def register_json(self, details):
        try:
            details = loads(details)
        except decoder.JSONDecodeError:
            return 500, {'text': 'parameter is bad JSON'}
        if type(details) != dict:
            return 500, {'text': 'bad parameters, not JSON'}
        if self.register(details):
            return 200, {'text': 'endpoint registered successfully'}
        return 500, {'text': 'invalid endpoint details'}


class Route(object):

    def __init__(self, details, key):
        """
        Create a new route object

        :param details: Details of the route
        :param key: Index into the hosts table
        """
        self._lastseen = datetime.now()
        self._proto = details['protocol']
        self._host = details['host']
        self._port = int(details['port'])
        self._uri = details['uri']
        self._ui = self._uri.rstrip('/').split('/')[-1] == 'ui'

    @property
    def path(self):
        return self._uri

    @property
    def txt(self):
        return '{}://{}:{}{}'.format(self._proto, self._host, self._port, self._uri)

    @property
    def proto(self):
        return self._proto

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return int(self._port)

    @property
    def uri(self):
        return self._uri.encode()

    @property
    def ssl(self):
        return self._proto == 'https'

    @property
    def is_ui(self):
        return self._ui

    def ping(self):
        self._last = datetime.now()
        print("--", self._last)

    @property
    def is_local(self):
        return self._port == 8079 and self._host == 'localhost'

    @property
    def last_seen(self):
        if self.is_local:
            return 'Always Online'
        return self._last #.strftime('%c')

    @property
    def status(self):
        return "OK"
        if timedelta(datetime.now(), self._last) < 8:
            return "UP"
        return "DOWN"

if 'router' not in globals():
    router = Router()

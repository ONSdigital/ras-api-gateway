##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from .proxy_tools import ProxyTools
from .route import Route
from json import loads, dumps, decoder
from datetime import datetime
from ons_ras_common import ons_env


class Router(ProxyTools):

    def __init__(self):
        """
        Initialise our main structures
        """
        self._host_table = {}
        self._route_table = {}

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

    def register(self, details):
        """
        Register an endpoint

        :param details: Details of the endpoint (dict)
        :return: Boolean
        """
        for attribute in ['protocol', 'host', 'port', 'uri']:
            if attribute not in details:
                self.info("attribute '{}' is missing".format(attribute))
                return False

        self.add(Route(
            details['protocol'],
            details['host'],
            int(details['port']),
            details['uri']
        ))
        self.log('registered "{uri}"'.format(**details))
        key = '{}:{}'.format(details['host'], details['port'])
        self._hosts[key] = datetime.now()
        return True

    def add(self, route):
        self.routing_table[route.uri.decode()] = route


class xRouter(ProxyTools):

    def __init__(self):
        self.routing_table = {}
        self._hosts = {}

    def setup(self):
        self.register(dumps({
            'protocol':'http',
            'host': 'localhost',
            'port': '5000',
            'uri': '/'
        }))
        for endpoint in ['register', 'unregister', 'status', 'ui/', 'ui/css', 'ui/lib',
                         'ui/images', 'swagger.json', 'mygateway', 'ping', 'surveys/todo', 'benchmark']:
            self.register(dumps({
                'protocol': 'http',
                'host': 'localhost',
                'port': '8079',
                'uri': '/api/1.0.0/'+endpoint
            }))


    def add(self, route):
        self.routing_table[route.uri.decode()] = route


    def register(self, details):
        try:
            details = loads(details)
        except decoder.JSONDecodeError:
            return 500, {'text': 'parameter is bad JSON'}

        if type(details) != dict:
            return 500, {'text': 'bad parameters, not JSON'}
        for attribute in ['protocol', 'host', 'port', 'uri']:
            if attribute not in details:
                return 500, {'text': "attribute '{}' is missing".format(attribute)}

        self.add(Route(
            details['protocol'],
            details['host'],
            int(details['port']),
            details['uri']
        ))
        print('registered "{uri}"'.format(**details))
        key = '{}:{}'.format(details['host'], details['port'])
        self._hosts[key] = datetime.now()
        return 200, {'text': 'endpoint registered successfully'}

    def add(self, route):
        self.routing_table[route.uri.decode()] = route

    def route(self, uri):
        parts = uri.split('?')[0].split('/')
        while len(parts):
            test = '/'.join(parts)
            if test in self.routing_table:
                return self.routing_table[test]
            if test+'/' in self.routing_table:
                return self.routing_table[test + '/']
            parts.pop()
        return None

    def status(self):
        routes = []
        for _, route in self.routing_table.items():
            routes.append(route.txt())
        return 200, {'routes': routes}

    def ping(self, host, port):
        for route in self.routing_table.values():
            print("@@@@@@@@@@",host,port, route.is_ui, route.txt)
            if route.port == port and route.host == host and route.is_ui:
                route.ping()
                return 200, 'OK'

        return 204, 'not registered'

router = Router()

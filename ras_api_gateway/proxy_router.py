##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from .proxy_tools import ProxyTools
from json import loads, dumps, decoder
from datetime import datetime

class Route(object):

    def __init__(self, proto, host, port, uri):
        self._proto = proto
        self._host = host
        self._port = port
        self._uri = uri
        self._ui = uri.rstrip('/').split('/')[-1] == 'ui'

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


class Router(ProxyTools):

    def __init__(self):
        self.routing_table = {}
        self._hosts = {}

    def last_seen(self, route):
        key = '{}:{}'.format(route.host, route.port)
        if key not in self._hosts:
            return "Not seen yet"
        return self._hosts[key].strftime('%c')

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
        key = '{}:{}'.format(host, port)
        if key in self._hosts:
            self._hosts[key] = datetime.now()
            return 200, 'OK'
        else:
            return 204, 'not registered'

router = Router()

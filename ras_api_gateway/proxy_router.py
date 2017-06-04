##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from .proxy_tools import ProxyTools
from json import loads, dumps, decoder

class Route(object):

    def __init__(self, proto, host, port, uri):
        self._proto = proto
        self._host = host
        self._port = port
        self._uri = uri

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


class Router(ProxyTools):

    def __init__(self):
        self.routing_table = {}

    def setup(self):
        for endpoint in ['register', 'unregister', 'status', 'ui/', 'ui/css', 'ui/lib', 'ui/images', 'swagger.json']:
            self.register(dumps({
                'protocol': 'http',
                'host': 'localhost',
                'port': '8080',
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
        return 200, {'text': 'endpoint registered successfully'}

    def add(self, route):
        self.routing_table[route.uri.decode()] = route

    def route(self, uri):
        parts = uri.split('/')
        while len(parts):
            test = '/'.join(parts)
            if test in self.routing_table:
                return self.routing_table[test]
            if test+'/' in self.routing_table:
                return self.routing_table[test+'/']
            parts.pop()
        for line in self.routing_table:
            print(line)
        return None

    def status(self):
        routes = []
        for _, route in self.routing_table.items():
            routes.append(route.txt())
        return 200, {'routes': routes}


router = Router()

##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from datetime import datetime
from json import loads, decoder
from ons_ras_common import ons_env


class Router(object):

    def __init__(self):
        self._hosts = {}
        self._endpoints = {}

    def info(self, text):
        ons_env.logger.info('[router] {}'.format(text))

    def activate(self):
        self.info('Router is running on port "{}"'.format(ons_env.port))
        for endpoint in ['register', 'ping']:
            self.register({
                'protocol': ons_env.get('flask_protocol'),
                'host': ons_env.get('flask_host'),
                'port': ons_env.get('flask_port'),
                'uri': '/api/1.0.0/{}'.format(endpoint)
            })
        self._hosts = {}

    def route(self, uri):
        parts = uri.split('?')[0].split('/')
        while len(parts):
            test = '/'.join(parts)
            if test in self._endpoints:
                return self._endpoints[test]
            if test+'/' in self._endpoints:
                return self._endpoints[test + '/']
            parts.pop()

        print("NO MATCH")
        return None

    def ping(self, host, port):
        key = '{}:{}'.format(host, port)
        if key in self._hosts:
            if self._hosts[key].alive():
                self._hosts[key].ping()
                return 200, 'OK'
        return 204, 'not registered'

    def register(self, details):
        """
        Register an endpoint

        :param details: Details of the endpoint (dict)
        """
        for attribute in ['protocol', 'host', 'port', 'uri']:
            if attribute not in details:
                self.info("attribute '{}' is missing".format(attribute))
                return False

        return self.update(details)

    def update(self, details):
        """
        Add a new endpoint

        :param details: Endpoint details
        :return: Boolean
        """
        key = '{host}:{port}'.format(**details)
        route = Route(details, key)
        self._endpoints[route.path] = route
        if key not in self._hosts and route.is_ui:
            self._hosts[key] = route

        self.info('registered "{uri}"'.format(**details))
        return True

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

    @property
    def host_list(self):
        items = []
        proto = ons_env.get('protocol')
        host = ons_env.get('api_gateway')
        port = 443 if proto == 'https' else 8080
        for route in self._hosts.values():
            #base = '{}://{}:{}'.format(proto, host, port)
            base = '{}://{}:{}'.format(
                ons_env.get('api_protocol'),
                ons_env.get('api_host'),
                ons_env.get('api_port')
            )
            items.append([
                'Unknown microservice',
                '<a href="{}{}">{}</a>'.format(base, route.uri.decode(), route.uri.decode()),
                '{}:{}'.format(route.host, route.port),
                route.last_seen,
                route.status_label
            ])
        return items

    @property
    def route_list(self):
        items = []
        for route in self._endpoints.values():
            url = '{}://{}:{}{}'.format(route.proto, route.host, route.port, route.uri.decode())
            items.append(url)
        return items

    def expire(self):
        self.info('running expire')
        for route in self._hosts.values():
            if route.status != 'UP':
                to_delete = []
                for key, val in self._endpoints.items():
                    if route.host == val.host and route.port == val.port:
                        route.kill()
                        to_delete.append(key)

                self.log('deleting "{}" endpoints for "{}"'.format(len(to_delete), route.host))
                for key in to_delete:
                    del self._endpoints[key]


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
        self._alive = True

    def kill(self):
        self._alive = False

    def alive(self):
        return self._alive

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

    @property
    def is_local(self):
        return self._port == 8079 and self._host == 'localhost'

    def ping(self):
        self._lastseen = datetime.now()
        self._alive = True

    @property
    def last_seen(self):
        return self._lastseen.strftime('%c')

    @property
    def status(self):
        if (datetime.now() - self._lastseen).seconds < 8:
            return "UP"
        return "DOWN"

    @property
    def status_label(self):
        if (datetime.now() - self._lastseen).seconds < 8:
            label = 'success'
            badge = 'Up'
        else:
            label = 'danger'
            badge = 'Down'
        return '<span class ="label label-{}">{}</span>'.format(label, badge)


if 'router' not in globals():
    router = Router()

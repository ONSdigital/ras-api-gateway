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

#
#   This module contains the "Router" and "Route" classes. These have been the
#   subject of much iteration and could do with a little more rationalisation
#   and refactoring.
#

class Router(object):

    def __init__(self):
        self._hosts = {}
        self._endpoints = {}
        self._hits = 0

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
                route = self._endpoints[test]
                route.hit()
                self._hits += 1
                return route
            if test+'/' in self._endpoints:
                route = self._endpoints[test + '/']
                route.hit()
                self._hits += 1
                return route
            parts.pop()

        return None

    def ping(self, host, port):
        if port == "None":
            key = host
        else:
            key = '{}:{}'.format(host, port)
        if key in self._hosts:
            if self._hosts[key].alive:
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
        if 'key' in details:
            key = details['key']
        else:
            key = '{host}:{port}'.format(**details)

        route = Route(details, key)
        self._endpoints[route.path] = route
        if route.is_ui:
            self._hosts[key] = route

        self.info('registered "{}" "{uri}"'.format(key, **details))
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
        for key in sorted(self._hosts):
            route = self._hosts[key]
            #
            #   For local, we want to point to localhost:8080/path
            #   For CF we want (public-gw)/path
            #
            if ons_env.api_host == 'localhost' and int(ons_env.api_port) not in [80, 443]:
                base = 'http://{}:{}'.format(route.host, route.port)
            else:
                base = 'http://{}'.format(route.host)

            items.append([
                '<a target="_blank" href="{}{}">{}</a>'.format(base, route.uri.decode(), route.name),
                '{}:{}'.format(route.host, route.port),
                route.last_seen,
                route.status_label
            ])
        return items

    @property
    def route_list(self):
        items = []
        for key, route in self._endpoints.items():
            url = '{} ==>> {}://{}:{}{}'.format(key, route.proto, route.host, route.port, route.uri.decode())
            items.append(url)
        return items

    def expire(self):
        for key, route in self._hosts.items():
            if route.status != 'UP':
                to_delete = []

                for path, val in self._endpoints.items():
                    if key == val.key:
                        route.kill()
                        to_delete.append(path)

                if len(to_delete):
                    self.info('[expire task] deleting "{}" endpoints for "{}"'.format(len(to_delete), key))
                    for item in to_delete:
                        del self._endpoints[item]

                    self._hosts[key].kill()


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
        self._name = details.get('name', 'No Name')
        self._key = details.get('key', None)
        self._ui = self._uri.rstrip('/').split('/')[-1] == 'ui' or details.get('ui', False)
        self._alive = True
        self._hits = 0

    def hit(self):
        self._hits += 1

    def kill(self):
        self._alive = False

    @property
    def alive(self):
        return self._alive

    @property
    def key(self):
        return self._key

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
    def name(self):
        return self._name

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

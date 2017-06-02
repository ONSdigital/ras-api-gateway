##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from twisted.internet import ssl

class Route(object):

    def __init__(self, proto, host, port, ssl, uri):
        self._proto = proto
        self._host = host
        self._port = port
        self._ssl = ssl
        self._uri = uri

    @property
    def proto(self):
        return self._proto

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def ssl(self):
        return self._ssl

    @property
    def uri(self):
        return self._uri.encode()

    @property
    def url(self):
        return "{}://{}:{}{}".format(self._proto, self._host, self._port, self._uri).encode()


class Router(object):

    def __init__(self):

        self.routing_table = {}
        self.add(Route('https', 'linux.co.uk', 443, True, '/documentation/'))
        self.add(Route('http', 'linux.co.uk', 80, False, '/category/blogs'))
        self.add(Route('http', 'linux.co.uk', 80, False, '/category/distros'))
        self.add(Route('http', 'linux.co.uk', 80, False, '/mushrooms'))
        self.add(Route('https', 'ras-collection-instrument.apps.mvp.onsclofo.uk', 443, True, '/collection-instrument-api/1.0.2/ui/'))
        self.add(Route('https', 'ras-collection-instrument.apps.mvp.onsclofo.uk', 443, True, '/'))
        #self.add(Route('http', 'localhost', 8082, False, '/collection-instrument-api/1.0.2/ui/'))

    def add(self, route):
        self.routing_table[route.uri.decode()] = route

    def route(self, uri):
        return self.routing_table.get(uri.decode().split('?')[0], None)


router = Router()

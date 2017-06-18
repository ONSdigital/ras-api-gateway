##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from datetime import datetime, timedelta

class Route(object):

    def __init__(self, proto, host, port, uri):
        self._proto = proto
        self._host = host
        self._port = port
        self._uri = uri
        self._last = None
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


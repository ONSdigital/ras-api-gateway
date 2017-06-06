##############################################################################
#                                                                            #
#   ONS / RAS API Gateway                                                    #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
##############################################################################
from sys import _getframe
from twisted.python import log


class ProxyTools(object):

    def syslog(self, msg, dummy=None):
        """
        Report an issue to the external logging infrastructure
        :param lvl: The log level we're outputting to
        :param msg: The message we want to log
        :return:
        """
        line = _getframe(1).f_lineno
        name = _getframe(1).f_code.co_name
        log.msg("{}: #{} - {}".format(name, line, msg))
        return False

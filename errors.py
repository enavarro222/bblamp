#-*- coding:utf-8 -*-
""" custom errors
"""

class BBLampException(Exception):
    # cf http://flask.pocoo.org/docs/patterns/apierrors/
    status_code = 500

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
        self.data = {}

    def to_dict(self):
        rv = dict()
        rv['error'] = self.__class__.__name__
        rv['message'] = self.message
        rv['data'] = self.data
        return rv


class InvalidLappName(BBLampException):
    def __init__(self, message, lapp_name=None):
        self.status_code = 406 #Not Acceptable
        BBLampException.__init__(self, message)
        self.data["lapp_name"] = lapp_name


class LappAlreadyExist(BBLampException):
    def __init__(self, lapp_name):
        self.status_code = 406
        message = "Lamp app '%s' already exist" % lapp_name
        BBLampException.__init__(self, message)
        self.data["lapp_name"] = lapp_name


class LappDoNotExist(BBLampException):
    def __init__(self, lapp_name):
        self.status_code = 404 # Not Found
        message = "Lamp app '%s' doesn't exist" % lapp_name
        BBLampException.__init__(self, message)
        self.data["lapp_name"] = lapp_name


class LappRunning(BBLampException):
    def __init__(self, lapp_info):
        self.status_code = 406
        message = "A lamp app is already running"
        BBLampException.__init__(self, message)
        self.data.update(lapp_info)


class LappNotRunning(BBLampException):
    def __init__(self):
        self.status_code = 406
        message = "No lamp app running"
        BBLampException.__init__(self, message)



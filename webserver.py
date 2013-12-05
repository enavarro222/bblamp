#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
import sys
import json
import subprocess
import glob

# Make sure your gevent version is >= 1.0
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from flask import Flask, Response
from flask import render_template, jsonify

from utils import read_lapp_pidfile

# the Flask app
bblamp_app = Flask(__name__)
bblamp_app.debug = True

# app constants
BASEDIR = os.path.dirname(os.path.abspath(__file__))
LAPP_DIR = os.path.join(BASEDIR, "lapp/")
LAPP_USER = "navarro"
#LAPP_USER = "pi"
LAPP_OUTDIR = os.path.join(BASEDIR, "lapp_output/")
LAPP_OUTFILE = os.path.join(LAPP_OUTDIR, "lapp.stdout")
LAPP_LOGFILE = os.path.join(LAPP_OUTDIR, "lapp.log")
LAPP_PIDFILE = os.path.join(LAPP_OUTDIR, "lapp.pid")

# app shared state variables
subscriptions = []

#-------------------------------------------------------------------------------
# SSE "protocol
class ServerSentEvent(object):
    """ SSE "protocol" is described here: 
    https://developer.mozilla.org/en-US/docs/Server-sent_events/Using_server-sent_events
    """

    def __init__(self, data):
        self.data = data
        self.event = None
        self.id = None
        self.desc_map = {
            self.data : "data",
            self.event : "event",
            self.id : "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k) 
                 for k, v in self.desc_map.iteritems() if k]
        return "%s\n\n" % "\n".join(lines)


#-------------------------------------------------------------------------------
# custom errors
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


@bblamp_app.errorhandler(BBLampException)
def handle_invalid_lapp_name(error):
    """ BBLampException handler
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#-------------------------------------------------------------------------------
# lapp API

#TODO:
# create a new lapp
# update a lapp
# get a lapp from name
# parse a request to get a lapp data and metadata

# LAPPNAME.info associé a chaque lapp 
# cf :http://docs.python.org/2/library/configparser.html
# from_blockly = True/False
# author = ...
# comment = ...

# si "from_blocky" => LAPPNAME.by associé a chaque lapp

class LampApp(object):
    """ Set of function to manage lapp
    """

    @staticmethod
    def _lapp_valid_name(lapp_name):
        """ Check wheter it is a valid lamp app name

        Warning: do not check if the lapp exist or not.
        """
        # check name is corect
        if lapp_name.startswith("_"):
            raise InvalidLappName(
                "lapp name shouldn't starts with '_'",
                lapp_name=lapp_name
            )
        elif "." in lapp_name:
            raise InvalidLappName(
                "lapp name shouldn't use '.'",
                lapp_name=lapp_name
            )
        return True

    def __init__(self, lapp_name):
        self._lapp_valid_name(lapp_name)
        self.name = lapp_name
        self.py_code = None
        self.by_code = None
        self.from_blockly = False
        self.author = None
        self.comment = None
        self.creation_date = None
        self.modification_date = None

    def python_filname(self):
        """ Get the python script filename from a given lapp name
        """
        return os.path.join(LAPP_DIR, self.name + ".py")

    def exist(self):
        """ check wheter a lamp app exist or not
        """
        return os.path.isfile(self.python_filname())

    def create(self):
        #TODO
        pass

    def update(self):
        pass

    def load(self):
        # check exist
        if not self.exist():
            raise LappDoNotExist(self.name)
        # load .info
        # load .py
        with open(self.python_filname, "r") as lapp_file:
            self.py_code = lapp_file.read()
        # load .bly if any
        

    def encode(self):
        """ return a python (jsonable) representation of the lapp
        """
        lapp = {}
        lapp["name"] = self.name
        return lapp

@bblamp_app.route("/lapps/<string:lapp_name>", methods=["GET"])
def lapps_get(lapp_name):
    """ get the code of a program
    """
    lapp = LampApp(lapp_name)
    # load the file
    lapp.load()
    return jsonify(lapp.encode())

@bblamp_app.route("/lapps/<string:lapp_name>", methods=["DELETE"])
def lapps_delete(lapp_name):
    if not lapp_exist(lapp_name):
        raise LappDoNotExist(lapp_name)
    filename = lappname_to_filname(lapp_name)
    os.remove(filename)
    return '', 204

@bblamp_app.route("/lapps/<string:lapp_name>", methods=["PUT"])
def lapps_put(lapp_name):
    """ Create or update a lapp
    """
    result = {}
    # check doesn't already exist
    if lapp_exist(lapp_name):
        # update
        raise LappAlreadyExist(lapp_name)
        result["new"] = False
    else:
        # create the new file
        open(lappname_to_filname(lapp_name), 'a').close()
        result["new"] = True
    #result["lapp"] = {}
    response = jsonify(result)
    response.status_code = 201
    return response

@bblamp_app.route("/lapps", methods=["GET"])
def lapps_list_get():
    """ Return the list of existing lapp
    """
    lapp_list = glob.glob("%s/*.py" % LAPP_DIR)
    bname = os.path.basename
    splitext = os.path.splitext
    lapp_list = [splitext(bname(lapp_filename))[0] \
                        for lapp_filename in lapp_list]
    lapp_list = [lapp_name for lapp_name in lapp_list \
                        if not lapp_name.startswith("_") ]
    return jsonify(lapps = lapp_list)


#-------------------------------------------------------------------------------
# lapp ctrl API

@bblamp_app.route("/ctrl/run/<lapp_name>")
def lapp_run(lapp_name):
    """ Run a given lapp
    """
    # check name ok
    _lapp_valid_name(lapp_name)
    #check program exist
    if not _lapp_exist(lapp_name):
        raise LappDoNotExist(lapp_name)
    # check nothing running
    lapp_info = read_lapp_pidfile(LAPP_PIDFILE)
    if lapp_info is not None:
        raise LappRunning(lapp_info)
    # start daemon
    lapp_py = _lappname_to_filname(lapp_name)
    cmd = ["start-stop-daemon", "--start"]
    cmd += ["--background"] #comment it for debug
    cmd += ["--pidfile", LAPP_PIDFILE]
    cmd += ["--exec", "/usr/bin/python"]
    cmd += ["--user", "%s" % LAPP_USER]
    cmd += ["--chdir", "%s" % BASEDIR]
    cmd += ["--", "%s" % lapp_py]
    cmd += ["--pidfile", "%s" % LAPP_PIDFILE]
    cmd += ["--outfile", "%s" % LAPP_OUTFILE]
    cmd += ["--logfile", "%s" % LAPP_LOGFILE]
    #print(cmd)
    #print(" ".join(cmd))
    # setup python path
    varenv = os.environ.copy()
    varenv["PYTHONPATH"] = varenv.get("PYTHONPATH", "") + ":./"
    # run the program
    proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=varenv
        )
    output, error = proc.communicate()
    #print output
    #print error
    retcode = proc.poll()
    if retcode != 0:
        raise RuntimeError(error)
    #TODO update status (msg)
    ## check what running (if any)
    ## send msg
    return "done"

@bblamp_app.route("/ctrl/stop")
def lapp_stop():
    """ Stop the curently running lapp (if any)
    """
    # check nothing running
    lapp_info = read_lapp_pidfile(LAPP_PIDFILE)
    if lapp_info is None:
        raise LappNotRunning()
    # stop the lapp daemon
    cmd = ["start-stop-daemon", "--stop"]
    cmd += ["--pidfile", LAPP_PIDFILE]
    #print(cmd)
    #print(" ".join(cmd))
    proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    output, error = proc.communicate()
    retcode = proc.poll()
    if retcode != 0:
        raise RuntimeError(error)
    return "done"

def get_lapp_status():
    """ Return the status of the running lapp
    """
    output = {}
    output["status"] = "stopped"
    lappinfo = read_lapp_pidfile(LAPP_PIDFILE)
    if lappinfo is not None:
        output.update(lappinfo)
        output["status"] = "running"
    return output

@bblamp_app.route("/ctrl/status")
def lapp_status():
    """ Return the status of the running lapp (json data)
    """
    return jsonify(get_lapp_status())

#-------------------------------------------------------------------------------
# lapp log API (push)

@bblamp_app.route("/log/debug")
def log_debug():
    return "Currently %d subscriptions" % len(subscriptions)

@bblamp_app.route("/log/subscribe")
def log_subscribe():
    def gen():
        q = Queue()
        subscriptions.append(q)
        try:
            while True:
                result = q.get()
                ev = ServerSentEvent(str(result))
                yield ev.encode()
        except GeneratorExit: # Or maybe use flask signals
            subscriptions.remove(q)

    return Response(gen(), mimetype="text/event-stream")

def send_data(dtype, data):
    """ Send data to the clients
    """
    output = {
        "dtype": dtype,
        "data": data
    }
    for sub in subscriptions[:]:
        print("%s : %s" % (dtype, data))
        sub.put(json.dumps(output))

def new_lapp_output(msg):
    send_data("output", msg)

def new_lapp_logmsg(msg):
    send_data("log", msg)

def new_lapp_status():
    send_data("status", get_lapp_status())

def monitor_logging_file(filename, output_fct):
    """ pseudo therad (gevent) that monitor a log file
    """
    while True:
        try:
            with open(filename, "r") as in_file:
                #seek to the end
                # in order to not send all already in the file lines
                in_file.seek(0, os.SEEK_END)
                while True:
                    # check the file still exist
                    # cf: http://stackoverflow.com/a/12690767
                    if os.fstat(in_file.fileno()).st_nlink == 0:
                        break
                    # try to read next line
                    nextline = in_file.readline()
                    if nextline:
                        output_fct(nextline)
                    # wait some time
                    gevent.sleep(0.1)
        except IOError as error:
            # file doesn't exist or not
            if error.errno == 2:
                #TODO: add logging
                gevent.sleep(1)
            else:
                raise

def monitor_lapp_logfile():
    monitor_logging_file(LAPP_LOGFILE, new_lapp_logmsg)

def monitor_lapp_outfile():
    monitor_logging_file(LAPP_OUTFILE, new_lapp_output)

def monitor_lapp_status():
    while True:
        last_status = get_lapp_status()
        while last_status == get_lapp_status():
                gevent.sleep(0.4)
        new_lapp_status()
        gevent.sleep(0.4)

#-------------------------------------------------------------------------------
# single page app getter
@bblamp_app.route("/")
def main_page():
    return render_template("index.html")

@bblamp_app.route("/ltest")
def logging_test():
    return render_template("log_test.html")

#-------------------------------------------------------------------------------
def main():
    print("<run>")
    # file monitoring
    monitor_log_worker = gevent.spawn(monitor_lapp_logfile)
    monitor_output_worker = gevent.spawn(monitor_lapp_outfile)
    monitor_status_worker = gevent.spawn(monitor_lapp_status)
    # web server
    server = WSGIServer(("0.0.0.0", 5000), bblamp_app)
    server.serve_forever()
    print("<run_done>")
    return 0

if __name__ == "__main__":
    sys.exit(main())

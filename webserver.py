#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
import sys
import json
import subprocess

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
#LAPP_USER = "navarro"
LAPP_USER = "pi"
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
        BBLampException.__init__(self, message)
        self.data["lapp_name"] = lapp_name


class LappAlreadyExist(BBLampException):
    def __init__(self, lapp_name):
        message = "Lamp app '%s' already exist" % lapp_name
        BBLampException.__init__(self, message)
        self.data["lapp_name"] = lapp_name


class LappDoNotExist(BBLampException):
    def __init__(self, lapp_name):
        message = "Lamp app '%s' doesn't exist" % lapp_name
        BBLampException.__init__(self, message)
        self.data["lapp_name"] = lapp_name


class LappRunning(BBLampException):
    def __init__(self, lapp_info):
        message = "A lamp app is already running"
        BBLampException.__init__(self, message)
        self.data.update(lapp_info)

class LappNotRunning(BBLampException):
    def __init__(self):
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
# lapp_name helper
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
    return True

def _lappname_to_filname(lapp_name):
    """ Get the python script filename from a given lapp name
    """
    _lapp_valid_name(lapp_name)
    return os.path.join(LAPP_DIR, lapp_name + ".py")

def _lapp_exist(lapp_name):
    """ check wheter a lamp app exist or not
    """
    return os.path.isfile(_lappname_to_filname(lapp_name))

#-------------------------------------------------------------------------------
# lapp API

@bblamp_app.route("/lapp/new/<lapp_name>")
def new_program(lapp_name):
    """ create a new program
    """
    output = {}
    # check doesn't already exist
    if _lapp_exist(lapp_name):
        raise LappAlreadyExist(lapp_name)
    # create the new file
    open(_lappname_to_filname(lapp_name), 'a').close()
    return jsonify(output)

@bblamp_app.route("/lapp/get/<lapp_name>")
def get_program(lapp_name):
    """ get the code of a program
    """
    output = {}
    # check exist
    if not _lapp_exist(lapp_name):
        raise LappDoNotExist(lapp_name)
    # load the file
    with open(_lappname_to_filname(lapp_name), "r") as lapp_file:
        output["code"] = lapp_file.read()
    # extract metadata
    #TODO
    return jsonify(output)

@bblamp_app.route("/lapp/list")
def list_program():
    """ list all avaliable lamp apps
    """
    #TODO
    pass

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

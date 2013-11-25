#!/usr/bin/python
#-*- coding:utf-8 -*-
import subprocess
import sys
import os
import signal
import time

# Make sure your gevent version is >= 1.0
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from flask import Flask, Response
from flask import render_template, jsonify

# the Flask app
app = Flask(__name__)
app.debug = True

# app constants
LOG_PID_PATH = "running_prog.pid"
LAPP_BASEDIR = "./lapp/"

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


@app.errorhandler(BBLampException)
def handle_invalid_lapp_name(error):
    """ BBLampException handler
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

#-------------------------------------------------------------------------------
# lapp_name helper
def _lapp_valid_name(lapp_name):
    """ check wheter it is a valid lamp app name
    """
    if lapp_name.startswith("_"):
        raise InvalidLappName(
            "lapp name shouldn't starts with '_'",
            lapp_name=lapp_name
        )
    return True

def _lappname_to_filname(lapp_name):
    _lapp_valid_name(lapp_name)
    return os.path.join(LAPP_BASEDIR, lapp_name + ".py")

def _lapp_exist(lapp_name):
    """ check wheter a lamp app exist or not
    """
    return os.path.isfile(_lappname_to_filname(lapp_name))

@app.route("/lapp/new/<lapp_name>")
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

#-------------------------------------------------------------------------------
# lapp API

@app.route("/lapp/get/<lapp_name>")
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


@app.route("/lapp/list")
def list_program():
    """ list all avaliable lamp apps
    """
    #TODO
    pass


#-------------------------------------------------------------------------------
# lapp ctrl API

@app.route("/ctrl/run/<lapp_name>")
def lapp_run(lapp_name):
    """ Run a given lapp
    """
    # check name ok
    _lapp_valid_name(lapp_name)
    # check program exist
    #TODO better check : if file but no process
    if(os.path.isfile(LOG_PID_PATH) == True):
        #XXX : gestion de l'erreur non uniforme
        return "program already running"
    # run the program
    with open(LOG_PID_PATH, "w") as pid_file:
        lapp_py = _lappname_to_filname(lapp_name)
        print "starting log process: ", lapp_py
        proc = subprocess.Popen(
                ["python", "%s" % lapp_py],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                #shell=True,
                #preexec_fn=os.setsid
            )
        pid = proc.pid
        pid_file.write("%s\n" % (pid))
        pid_file.write("%s\n" % (lapp_name))
        pid_file.write("%s\n" % (lapp_py))
    # return
    #TODO json
    return "done:%d" % pid

@app.route("/ctrl/stop")
def lapp_stop():
    """ Stop the curently running lapp (if any)
    """
    if(os.path.isfile(LOG_PID_PATH) != True):
        #XXX : gestion de l'erreur non uniforme
        return "log process not started, can not find file: %s" % LOG_PID_PATH, 500
    # stop the program
    with open(LOG_PID_PATH, "r") as pid_file:
        try:
            pid = int(pid_file.readline())
        except ValueError:
            #XXX log error
            subprocess.call("rm " + LOG_PID_PATH, shell=True)
            pid = None
    
    print "pid = ", pid
    if pid is not None:
        try:
            os.killpg(pid, signal.SIGTERM) #kill process group
        except OSError as os_err:
            if os_err.errno == 3: # No such process
                print("PID file not up to date, removing it !")
                pass
            else:
                raise
        finally:
            subprocess.call("rm " + LOG_PID_PATH, shell=True)
    
    #TODO json
    return "done"

@app.route("/ctrl/status")
def lapp_status():
    output = {}
    if(os.path.isfile(LOG_PID_PATH) != True):
        output["status"] = "stopped"
    else:
        with open(LOG_PID_PATH, "r") as pid_file:
            output["pid"] = int(pid_file.readline())
            output["lapp_name"] = pid_file.readline().strip()
            output["lapp_py"] = pid_file.readline().strip()
        #TODO: check process really running
        output["status"] = "running"
    
    return jsonify(output)

#-------------------------------------------------------------------------------
# lapp log API (push)

@app.route("/log/debug")
def log_debug():
    return "Currently %d subscriptions" % len(subscriptions)

@app.route("/log/publish")
def log_publish():
    #Dummy data - pick up from request for real data
    def notify():
        msg = str(time.time())
        send_logline(msg)
    
    gevent.spawn(notify)
    return "OK"

@app.route("/log/subscribe")
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

def send_logline(logline):
    for sub in subscriptions[:]:
        print("msg sent : %s" % logline)
        sub.put(logline)

def monitor_logfile():
    with open("./inputfile") as in_file:
        #except serial.SerialException, e:
        #     yield 'event:error\n' + 'data:' + 'Serial port error({0}): {1}\n\n'.format(e.errno, e.strerror)
        #     messageid = messageid + 1
        while True:
            gevent.sleep(0.1)
            nextline = in_file.readline()
            if nextline:
                send_logline(nextline)

#-------------------------------------------------------------------------------
# single page app getter
@app.route("/")
def main():
    return render_template("index.html")

@app.route("/ltest")
def logging_test():
    return render_template("log_test.html")

if __name__ == "__main__":
    print("<run>")
    log_worker = gevent.spawn(monitor_logfile)
    server = WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()
    print("<run_done>")


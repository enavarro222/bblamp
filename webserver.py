#!/usr/bin/python
#-*- coding:utf-8 -*-
import os
import sys
import json

# Make sure your gevent version is >= 1.0
import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

from flask import Flask, Response
from flask import render_template, jsonify

from utils import ServerSentEvent

from api import lapps
from api import get_lapp_status
from errors import BBLampException

#TODO: hardware ?
from simulate import simu

import config

# the Flask app
bblamp_app = Flask(__name__)
bblamp_app.debug = True

# app API
bblamp_app.register_blueprint(lapps, url_prefix="/v1")

# lamp simulation API
bblamp_app.register_blueprint(simu, url_prefix="/simu/v1")

# app shared state variables
subscriptions = []


#-------------------------------------------------------------------------------

@bblamp_app.errorhandler(BBLampException)
def handle_invalid_lapp_name(error):
    """ BBLampException handler
    """
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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
                        break # try to reopen it if it has been deleted
                    # try to read next line
                    log_line = in_file.readline()
                    if log_line != "":
                        # Search if next lines are for the same log "line"
                        ## wait short time to be sure to not miss next "same log line"
                        gevent.sleep(2e-3)
                        last_pos = in_file.tell()
                        nextline = in_file.readline()
                        while not (nextline == "" or nextline.startswith("LampApp")): # = not a new log line
                            log_line += nextline
                            # wait short time to be sure to not miss next "same log line"
                            gevent.sleep(2e-3)
                            last_pos = in_file.tell()
                            nextline = in_file.readline()
                        # push log_line
                        output_fct(log_line)
                        # and seek back to the next log line (seek to the same position)
                        in_file.seek(last_pos)
                    gevent.sleep(0.1)
        except IOError as error:
            # file doesn't exist or not
            if error.errno == 2:
                #TODO: add logging
                gevent.sleep(1)
            else:
                raise

def monitor_lapp_logfile():
    monitor_logging_file(config.LAPP_LOGFILE, new_lapp_logmsg)

def monitor_lapp_outfile():
    monitor_logging_file(config.LAPP_OUTFILE, new_lapp_output)

def monitor_lapp_status():
    while True:
        last_status = get_lapp_status()
        while last_status["hash"] == get_lapp_status()["hash"]:
            gevent.sleep(0.4)
        new_lapp_status()
        gevent.sleep(0.4)

#-------------------------------------------------------------------------------
# single page app getter
@bblamp_app.route("/")
@bblamp_app.route("/<string:lapp_name>")
def main_page(lapp_name=None):
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

#!/usr/bin/python
#-*- coding:utf-8 -*-
import subprocess
import sys
import os
import signal

from flask import Flask
app = Flask(__name__)
app.debug = True

LOG_PID_PATH = "running_prog.pid"

def new_program():
    """ create a new program
    """
    pass

def list_program():
    """ list all avaliables programs
    """
    pass

def get_program():
    """
    """
    pass

@app.route("/ctr/run/<prog_name>")
def run_program(prog_name):
    """
    """
    # check program exist
    if(os.path.isfile(LOG_PID_PATH) == True):
        return "program already running"
    # stop program if needed
    # run the program
    with open(LOG_PID_PATH, "w") as pid_file:
        cmd = "top"
        print "starting log process: ", cmd
        proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                preexec_fn=os.setsid
            )
        pid = proc.pid
        pid_file.write("%s\n" % (pid))
        # return
    return "done:%d" % pid

@app.route("/ctr/stop")
def stop_program():
    """
    """
    if(os.path.isfile(LOG_PID_PATH) != True):
        return "log process not started, can not find file: %s" % LOG_PID_PATH
    # stop the program
    with  open(LOG_PID_PATH, "r") as pid_file:
        pid = int(pid_file.readline())
    print "pid = ", pid
    os.killpg(pid, signal.SIGTERM)
    subprocess.call("rm " + LOG_PID_PATH, shell=True)
    return "done"

@app.route("/")
def main():
    return "Hello World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0")

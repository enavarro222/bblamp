#-*- coding:utf-8 -*-
import os
import subprocess
import glob

from flask import Blueprint
from flask import jsonify

from utils import read_lapp_pidfile

from errors import InvalidLappName
from errors import LappDoNotExist, LappAlreadyExist
from errors import LappRunning, LappNotRunning

lapps = Blueprint('lapps', __name__)

BASEDIR = os.path.dirname(os.path.abspath(__file__))
LAPP_DIR = os.path.join(BASEDIR, "lapp/")
LAPP_USER = "navarro"
#LAPP_USER = "pi"
LAPP_OUTDIR = os.path.join(BASEDIR, "lapp_output/")
LAPP_OUTFILE = os.path.join(LAPP_OUTDIR, "lapp.stdout")
LAPP_LOGFILE = os.path.join(LAPP_OUTDIR, "lapp.log")
LAPP_PIDFILE = os.path.join(LAPP_OUTDIR, "lapp.pid")

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

    @staticmethod
    def _check_create_outdir():
        """ check that lapps output dir exist (create it if needed)
        """
        if not os.path.isdir(LAPP_OUTDIR):
            os.makedirs(LAPP_OUTDIR)

    @staticmethod
    def lapps_list():
        """ return the list of existing lapps
        """
        lapp_list = glob.glob("%s/*.py" % LAPP_DIR)
        bname = os.path.basename
        splitext = os.path.splitext
        lapp_list = [splitext(bname(lapp_filename))[0] \
                            for lapp_filename in lapp_list]
        lapp_list = [LampApp(lapp_name) for lapp_name in lapp_list \
                            if not lapp_name.startswith("_") ]
        return lapp_list

    def __init__(self, lapp_name):
        self._lapp_valid_name(lapp_name)
        # lapp name
        self.name = lapp_name
        # do the py code come from blockly
        self.from_blockly = False
        # author name
        self.author = None
        # description of the lapp
        self.comment = None
        # some date
        self.creation_date = None
        self.modification_date = None
        ## Code
        # python code, None if not yet readed
        self.py_code = None
        # blockly code, None if not yet readed or doesn't exist
        self.by_code = None
        #TODO:
        # load .info

    @property
    def python_filname(self):
        """ Get the python script filename from a given lapp name
        """
        return os.path.join(LAPP_DIR, self.name + ".py")

    @property
    def blockly_filname(self):
        """ Get the blockly script filename from a given lapp name
        """
        return os.path.join(LAPP_DIR, self.name + ".by")

    def exist(self):
        """ check wheter a lamp app exist or not
        """
        return os.path.isfile(self.python_filname)

    def create(self):
        """ Create a new lapp
        """
        if self.exist():
            raise LappAlreadyExist(self.name)
        # create python file
        with open(self.python_filname, "w") as pyfile:
            pyfile.write("#-*- coding:utf-8 -*-\n")

    def delete(self):
        """ Remove the lapp
        """
        if not self.exist():
            raise LappDoNotExist()
        # destroy python file
        os.remove(self.python_filname)
        #TODO: todo remove blockly file (if needed)
        #TODO: remove info file

    def update(self):
        pass

    def load_code(self):
        # check exist
        if not self.exist():
            raise LappDoNotExist(self.name)
        # load .py
        with open(self.python_filname, "r") as lapp_file:
            self.py_code = lapp_file.read()
        #TODO load .bly if any

    def encode(self):
        """ return a python (jsonable) representation of the lapp
        """
        lapp = {}
        lapp["id"] = self.name
        lapp["name"] = self.name
        lapp["from_blockly"] = self.from_blockly
        lapp["comment"] = self.comment
        lapp["author"] = self.author
        if self.py_code is not None:
            lapp["py_code"] = self.py_code
        if self.by_code is not None:
            lapp["by_code"] = self.by_code
        return lapp

    def run(self):
        """ run the lapp as a daemon
        """
        # check exist
        if not self.exist():
            raise LappDoNotExist(self.name)
        # check output dir exist (create it if needed)
        LampApp._check_create_outdir()
        # check nothing running
        lapp_info = read_lapp_pidfile(LAPP_PIDFILE)
        if lapp_info is not None:
            raise LappRunning(lapp_info)
        # start daemon
        cmd = ["start-stop-daemon", "--start"]
        cmd += ["--background"] #comment it for debug
        cmd += ["--pidfile", LAPP_PIDFILE]
        cmd += ["--exec", "/usr/bin/python"]
        cmd += ["--user", "%s" % LAPP_USER]
        cmd += ["--chdir", "%s" % BASEDIR]
        cmd += ["--", "%s" % self.python_filname]
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

    @staticmethod
    def stop():
        """ stiop the lapp (if running)
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

#-------------------------------------------------------------------------------
# lapp ressource API

@lapps.route("/lapps", methods=["GET"])
def get_list():
    """ Return the list of existing lapp
    """
    import gevent
    gevent.sleep(1); #XXX
    all_lapps = LampApp.lapps_list()
    all_lapps = [lapp.encode() for lapp in all_lapps]
    return jsonify(lapps=all_lapps)

@lapps.route("/lapps/<string:lapp_name>", methods=["GET"])
def get(lapp_name):
    """ get the code of a program
    """
    import gevent
    gevent.sleep(1.5); #XXX
    lapp = LampApp(lapp_name)
    # load the file
    lapp.load_code()
    return jsonify(lapp.encode())

@lapps.route("/lapps/<string:lapp_name>", methods=["DELETE"])
def delete(lapp_name):
    """ remove a lapp
    """
    lapp = LampApp(lapp_name)
    lapp.delete()
    return '', 204

@lapps.route("/lapps/<string:lapp_name>", methods=["PUT"])
def put(lapp_name):
    """ Create or update a lapp
    """
    result = {}
    lapp = LampApp(lapp_name)
    if lapp.exist():
        lapp.update()
        result["new"] = False
    else:
        # create the new lapp
        lapp.create()
        result["new"] = True
    response = jsonify(result)
    response.status_code = 201
    return response

#-------------------------------------------------------------------------------
# lapp ctrl API

@lapps.route("/ctrl/run/<lapp_name>")
def run(lapp_name):
    """ Run a given lapp
    """
    running_lapp = LampApp(lapp_name)
    running_lapp.run()
    return "done"

@lapps.route("/ctrl/stop")
def stop():
    """ Stop the curently running lapp (if any)
    """
    return LampApp.stop()

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

@lapps.route("/ctrl/status")
def status():
    """ Return the status of the running lapp (json data)
    """
    return jsonify(get_lapp_status())


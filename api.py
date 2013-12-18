#-*- coding:utf-8 -*-
import os
import subprocess
import glob
import json

from flask import Blueprint
from flask import request, abort, jsonify

import ConfigParser
from ConfigParser import SafeConfigParser

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

# LAPPNAME.info associé a chaque lapp 
# cf : http://docs.python.org/2/library/configparser.html
# from_blockly = True/False
# author = ...
# comment = ...

# si "from_blocky" => LAPPNAME.by associé a chaque lapp

class LampApp(object):
    """ Set of function to manage lapp
    """
    INFO_ATTRS = [
        # name, get cast fct, set cast fct
        ("author", None, None),
        ("comment", None, None),
        ("from_blockly", lambda x: x.lower() in ("yes", "true", "1"), str),
    ]
    INFO_SECTION = "lapp"
    
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
        lapp_list = glob.glob("%s/*.info" % LAPP_DIR)
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
        self.author = ""
        # description of the lapp
        self.comment = ""
        # some date
        self.creation_date = None
        self.modification_date = None
        self.info_saved = False
        # load .info
        if self.exist():
            self.load_info()

    @property
    def py_code(self):
        """ reads the python code of the lapp
        """
        with open(self.python_filname, "r") as pyfile:
            py_code = pyfile.read()
        return py_code

    @py_code.setter
    def py_code(self, py_code):
        """ writes a new version of the python code of the lapp
        """
        with open(self.python_filname, "w") as pyfile:
            pyfile.write(py_code)

    @property
    def by_code(self):
        """ reads the blokly code of the lapp
        """
        if not self.from_blockly:
            raise ValueError("This lapp is not build using blockly")
        with open(self.blockly_filname, "r") as byfile:
            by_code = byfile.read()
        return by_code

    @by_code.setter
    def by_code(self, by_code):
        """ writes a new version of the blockly code of the lapp
        """
        if not self.from_blockly:
            raise ValueError("This lapp is not build using blockly")
        with open(self.blockly_filname, "w") as byfile:
            byfile.write(by_code)

    def load_info(self):
        """ Reads lapp attributes from a config file
        """
        parser = SafeConfigParser()

        parser.read(self.info_filname)
        for attr_name, get_cast, _ in LampApp.INFO_ATTRS:
            try:
                value = parser.get(LampApp.INFO_SECTION, attr_name)
                if get_cast is not None:
                    value = get_cast(value)
                print(attr_name, value)
                setattr(self, attr_name, value)
            except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
                pass

    def save_info(self):
        """ Writes lapp attributes in a config file
        """
        parser = SafeConfigParser()
        parser.add_section(LampApp.INFO_SECTION)
        for attr_name, _, set_cast in LampApp.INFO_ATTRS:
            value = getattr(self, attr_name)
            if set_cast is not None:
                value = set_cast(value)
            parser.set(LampApp.INFO_SECTION, attr_name, value)
        with open(self.info_filname, "w") as infofile:
            parser.write(infofile)

    @property
    def info_filname(self):
        """ Get the filename of the info file 
        """
        return os.path.join(LAPP_DIR, self.name + ".info")

    @property
    def python_filname(self):
        """ Get the python script filename
        """
        return os.path.join(LAPP_DIR, self.name + ".py")

    @property
    def blockly_filname(self):
        """ Get the blockly script filename
        """
        return os.path.join(LAPP_DIR, self.name + ".by")

    def exist(self):
        """ check wheter a lamp app exist or not
        """
        return os.path.isfile(self.python_filname) \
                and os.path.isfile(self.info_filname)

    def create(self):
        """ Create a new lapp
        """
        if self.exist():
            raise LappAlreadyExist(self.name)
        # create config file
        self.save_info()
        # create python file
        self.py_code = "#-*- coding:utf-8 -*-\n"

    def delete(self):
        """ Remove the lapp
        """
        if not self.exist():
            raise LappDoNotExist()
        # remove info file
        os.remove(self.info_filname)
        # destroy python file
        os.remove(self.python_filname)
        #todo remove blockly file (if needed)
        if self.from_blockly:
            os.remove(self.blockly_filname)

    def update(self, new_vals):
        print(new_vals)
        for attr, get_cast, _ in LampApp.INFO_ATTRS:
            if attr in new_vals:
                value = new_vals[attr]
                setattr(self, attr, value)
        self.save_info()
        if "py_code" in new_vals:
            self.py_code = new_vals["py_code"]
        if "by_code" in new_vals:
            self.by_code = new_vals["by_code"]

    def encode(self):
        """ return a python (jsonable) representation of the lapp
        """
        # check exist
        if not self.exist():
            raise LappDoNotExist(self.name)
        lapp = {}
        lapp["id"] = self.name
        lapp["name"] = self.name
        lapp["from_blockly"] = self.from_blockly
        lapp["comment"] = self.comment
        lapp["author"] = self.author
        lapp["py_code"] = self.py_code
        if self.from_blockly:
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
    all_lapps = LampApp.lapps_list()
    all_lapps = [lapp.encode() for lapp in all_lapps]
    return jsonify(lapps=all_lapps)

@lapps.route("/lapps/<string:lapp_name>", methods=["GET"])
def get(lapp_name):
    """ get the code of a program
    """
    lapp = LampApp(lapp_name)
    # load the file
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
        if not request.headers['Content-Type'] == 'application/json':
            abort(415)
        data = request.json
        lapp.update(data)
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


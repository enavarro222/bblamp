#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import sys
import getpass

BASEDIR = os.path.dirname(os.path.abspath(__file__))

## user that run the applications
LAPP_USER = getpass.getuser()
    # default run the application with same user than the webserver...
    # you can change it here :
#LAPP_USER = "pi"

## path to the python interpreter used tu run application
LAPP_PYTHON = sys.executable
    # by default ^ : same as current interpreter (work with virtualenv)
#LAPP_PYTHON = "/usr/bin/python"

## dirs and file where to store runing application data
LAPP_DIR = os.path.join(BASEDIR, "user_apps/")
LAPP_OUTDIR = os.path.join(BASEDIR, "lapp_output/")
LAPP_OUTFILE = os.path.join(LAPP_OUTDIR, "lapp.stdout")
LAPP_LOGFILE = os.path.join(LAPP_OUTDIR, "lapp.log")
LAPP_PIDFILE = os.path.join(LAPP_OUTDIR, "lapp.pid")

## hardware configuration

from hardware.lamp import LedPixelsWebSimu
hardware = {
    "lamp": LedPixelsWebSimu(25),
}

## exemple harware for rpy led strip :

#from hardware.lamp import LedPixels
#from hardware.ar_i2c import ArI2C, ArBpRouge, ArSwBand, ArSwFct, ArVolume
#from hardware.ar_i2c import ArGauge

## declaration of available hardware
#hardware = {
#    "lamp": LedPixels(32),
#    "gauge": ArGauge(),
#    "bp_rouge": ArBpRouge(),
#    "sw_band": ArSwBand(),
#    "volume": ArVolume(),
#    "sw_fct": ArSwFct(),
#}

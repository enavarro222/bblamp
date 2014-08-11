#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))

#LAPP_USER = "navarro"
LAPP_USER = "pi"
LAPP_DIR = os.path.join(BASEDIR, "user_apps/")
LAPP_OUTDIR = os.path.join(BASEDIR, "lapp_output/")
LAPP_OUTFILE = os.path.join(LAPP_OUTDIR, "lapp.stdout")
LAPP_LOGFILE = os.path.join(LAPP_OUTDIR, "lapp.log")
LAPP_PIDFILE = os.path.join(LAPP_OUTDIR, "lapp.pid")


from hardware.lamp import LedPixels
from hardware.ar_i2c import ArI2C, ArBpRouge, ArSwBand, ArSwFct, ArVolume
from hardware.ar_i2c import ArGauge

# declaration of available hardware
hardware = {
    "lamp": LedPixels(32),
    "gauge": ArGauge(),
    "bp_rouge": ArBpRouge(),
    "sw_band": ArSwBand(),
    "volume": ArVolume(),
    "sw_fct": ArSwFct(),
}

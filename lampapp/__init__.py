#-*- coding:utf-8 -*-
import os
import sys
import logging
import argparse
import signal
import time

import gevent

#from ledpixels import LedPixelsFileStub as LedPixels
#from ledpixels import LedPixelsWebSimu as LedPixels
from ledpixels import LedPixels

from utils import read_lapp_pidfile, write_lapp_pidfile

class LampApp(object):
    NBPIXEL = 25

    def __init__(self):
        #logging
        self.debug = False  # if true exception aren't catched
        self.log = logging.getLogger("LampApp")
        # stdout (for self.print)
        self._stdout_filemane = None
        ## events callbacks
        self._setup_fct = None
        self._to_spawn = []

    def activate_lamp(self):
        """ make lamp (led pixels) available
        """
        self.lamp = LedPixels(self.NBPIXEL)
        self.lamp.off()

    def activate_wiimote(self):
        """ make wiimote available
        """
        from wiimote import Wiimote, WiimoteError
        self.wiimote = Wiimote()
        def check_reconnect():
            connected = False
            while True:
                # connect the wiimote
                if not self.wiimote.connected():
                    try:
                        print("connecting...")
                        self.wiimote.connect()
                        self.wait(0.4)
                        print("connected")
                    except WiimoteError:
                        print("connection fail")
                        self.wait(0.2)
                else:
                    self.wait(0.4)
        self._to_spawn.append(check_reconnect)

    def _run_log(self, fn):
        """ Run a fct and log exception (if any)
        """
        error = None
        try:
            fn()
        except Exception as err:
            self.log.exception("uncaught exception:")
            if self.debug:
                raise
            error = err
        return error

    def setup(self):
        """ Function decorator to declare an function to be run at start up
        """
        def setup_deco(fn):
            self._setup_fct = fn
            return fn
        return setup_deco
    
    def every(self, wait_time):
        """ Function decorator to declare an function to be run every indicaded
        """
        def every_deco(fn):
            def run_every():
                while True:
                    stime = time.time()
                    error = self._run_log(fn)
                    if error:
                        break
                    exec_time = time.time() - stime
                    # wait at least 20ms
                    self.wait(max(20e-3, wait_time-exec_time))
            self._to_spawn.append(run_every)
            return fn
        return every_deco
    
    def on(self, obj, event):
        """ Function decorator to declare an function to be run on an event
        """
        #TODO
        def on_deco(fn):
            return fn
        return on_deco
    
    def msg(self, msg):
        """ print a message
        """
        if self._stdout_filemane:
            with open(self._stdout_filemane, "a") as stdout:
                stdout.write("%s\n" % msg)

    def on_exit(self):
        if self.lamp:
            self.lamp.turn_off()
        sys.exit()

    def wait(self, time):
        gevent.sleep(time)

    def run(self):
        """ Run the lapp, ie:
        * setup and parse args
        * check if already running lapp with same pidfile
        * setup logging (for exception, at least)
        * setup output (self.msg)
        * write the pidfile

        and then :
        * call self.setup()
        * in a infinite loop, call self.loop()
        """
        # clean all at exit
        signal.signal(signal.SIGTERM, lambda signum, frame: self.on_exit())
        # cmd line argument parser
        parser = argparse.ArgumentParser(description='bb-lamp App.')
        outdir = "./lapp_output/"
        parser.add_argument(
            '--logfile', dest='logfile', type=str, default=outdir+"/lapp.log",
            help='path of the logging file'
            )
        parser.add_argument(
            '--outfile', dest='outfile', type=str, default=outdir+"/lapp.out",
            help='path for the output (print) file'
            )
        parser.add_argument(
            '--pidfile', dest='pidfile', type=str, default=outdir+"/lapp.pid",
            help='path of the PID file'
            )
        args = parser.parse_args()
        ## check PID file : only one lamp app at time
        running_lapp = read_lapp_pidfile(args.pidfile)
        if running_lapp is not None:
            print("Sorry, a lapp is already running !")
            for key, value in running_lapp.iteritems():
                print("%s: %s" % (key, value))
            raise SystemExit
        ## logging handler
        self.log.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fhandler = logging.FileHandler(args.logfile)
        fhandler.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
                '%(name)s:%(asctime)s:%(levelname)s:%(message)s'
            )
        fhandler.setFormatter(formatter)
        self.log.addHandler(fhandler)
        try:
            ## configure hardware
            self.activate_lamp()
            ## fill pid file
            write_lapp_pidfile(args.pidfile)
            ## out file for self.msg
            self._stdout_filemane = args.outfile
            ## run the lapp itself
            setup_error = None
            if self._setup_fct:
                setup_error = self._run_log(self._setup_fct)
            if not setup_error:
                jobs = [gevent.spawn(fn) for fn in self._to_spawn]
                gevent.joinall(jobs)
        except Exception:
            self.log.exception("uncaught exception:")
            raise
        finally:
            #
            pass


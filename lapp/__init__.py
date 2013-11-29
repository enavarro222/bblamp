#-*- coding:utf-8 -*-
import os
import logging
import argparse

from ledpixels import LedPixelsFileStub as LedPixels
from utils import read_lapp_pidfile, write_lapp_pidfile

class LampApp(object):
    NBPIXEL = 25

    def __init__(self):
        #logging
        self.log = logging.getLogger("LampApp")
        # stdout (for self.print)
        self._stdout_filemane = None
        ## "hardware" driver init
        #TODO make it configurable from "run"
        # init leds
        self.lamp = LedPixels(self.NBPIXEL)
        self.lamp.all_off()
        self.lamp.flush()

    def setup(self):
        raise NotImplementedError()

    def loop(self):
        raise NotImplementedError()

    def msg(self, msg):
        print(msg)
        if self._stdout_filemane:
            with open(self._stdout_filemane, "a") as stdout:
                stdout.write("%s\n" % msg)

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
        # cmd line argument parser
        parser = argparse.ArgumentParser(description='bb-lamp App.')
        parser.add_argument(
            '--logfile', dest='logfile', type=str, default="./lapp.log",
            help='path of the logging file'
            )
        parser.add_argument(
            '--outfile', dest='outfile', type=str, default="./lapp.out",
            help='path for the output (print) file'
            )
        parser.add_argument(
            '--pidfile', dest='pidfile', type=str, default="./lapp.pid",
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
                '%(asctime)s:%(name)s:%(levelname)s:%(message)s'
            )
        fhandler.setFormatter(formatter)
        self.log.addHandler(fhandler)
        try:
            ## fill pid file
            write_lapp_pidfile(args.pidfile)
            ## out file for self.msg
            self._stdout_filemane = args.outfile
            ## run the lapp itself
            self.setup()
            while True:
                self.loop()
        except Exception:
            self.log.exception("uncaught exception:")
            raise
        finally:
            #
            pass


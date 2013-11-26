#-*- coding:utf-8 -*-
import logging
import argparse

from ledpixels import LedPixelsFileStub as LedPixels
from utils import write_pidfile_or_die

class LampApp():
    NBPIXEL = 25

    def __init__(self):
        #logging
        self.log = logging.getLogger("LampApp")
        # stdout (for self.print)
        class StdOutStub():
            def write(self, txt):
                pass
        self.stdout = StdOutStub()
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
        self.stdout.write(msg)
        self.stdout.write("\n")

    def run(self):
        #argparse ?
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
        
        # PID file : only one lamp app at time
        write_pidfile_or_die(args.pidfile)

        # logging handler
        self.log.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        fh = logging.FileHandler(args.logfile)
        fh.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
        fh.setFormatter(formatter)
        self.log.addHandler(fh)
        
        #run
        try:
            with open(args.outfile, "w") as stdout:
                self.stdout = stdout
                self.setup()
                while True:
                    self.loop()
        except Exception as error:
            self.log.exception("uncaught exception:")
            raise

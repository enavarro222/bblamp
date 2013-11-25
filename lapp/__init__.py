#-*- coding:utf-8 -*-
from ledpixels import LedPixels


class LampApp():

    NBPIXEL = 25

    def __init__(self):
        #TODO: add logging
        # init leds
        self.lamp = LedPixels(self.NBPIXEL)
        self.lamp.all_off()
        self.lamp.flush()

    def setup(self):
        raise NotImplementedError()

    def loop(self):
        raise NotImplementedError()

    def run(self):
        # only one lamp app at time
        write_pidfile_or_die("./lapp.pid")
        self.setup()
        while True:
            self.loop()

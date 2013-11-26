#-*- coding:utf-8 -*-
import time

from lapp import LampApp

class MyLampApp(LampApp):

    def setup(self):
        self.on = False

    def loop(self):
        self.msg("Blink !")
        if self.on:
            self.lamp.all_off()
        else:
            self.lamp.all_on()
        self.lamp.flush()
        self.on = not self.on
        time.sleep(1)

if __name__ == "__main__":
    lapp = MyLampApp()
    lapp.run()

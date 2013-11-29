#-*- coding:utf-8 -*-
import time

from lapp import LampApp

class MyLampApp(LampApp):

    def setup(self):
        self.on = False
        self.count = 0

    def loop(self):
        # msg every 10 blink
        if self.count % 10 == 0:
            self.msg("still a live !")
        if self.count % 10 == 2:
            self.log.info("Log test !")
        self.count += 1
        # blink
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

#-*- coding:utf-8 -*-
import time
from random import randint, gauss
from colorsys import hls_to_rgb

from lapp import LampApp

def randColor(light, sat, mu=0.3, sigma=0.06):
    hue = gauss(mu, sigma)
    c = [hue%1,  light, sat]
    c = [int(255*val) for val in hls_to_rgb(*c)]
    return  c

class MyLampApp(LampApp):

    def setup(self):
        self.on = False
        self.count = 0

        #colorsys.hls_to_rgb(h, l, s)
        self.saturation = 0.7
        self.light = 0.1
        
        self.colors = [
            randColor(self.light, self.saturation, mu=0)
            for _ in range(0, 25)
        ]
        
    def loop(self):

        self.count += 1
        self.lamp.all_on()
        
        mu = (self.count/900.)%1
        # change one color:
        for _ in range(randint(0, 2)):
            k = randint(0, 24)
            self.colors[k] = randColor(self.light, self.saturation, mu=mu)
        
        for k in range(0, 25):
            color = self.colors[k]
            self.lamp.set_color(k, *color)
            #self.lamp.switch_on(self.position[k])
            

        self.lamp.flush()
        time.sleep(0.05)

if __name__ == "__main__":
    lapp = MyLampApp()
    lapp.run()
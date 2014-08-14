#-*- coding:utf-8 -*-
import time
from random import randint, gauss
from colorsys import hls_to_rgb

from lampapp import LampApp
from hardware.lamp import Color #FIXME odd import..

app = LampApp()
app.need("lamp")
app.need("volume")

def randColor(light, sat, mu=0.3, sigma=0.06):
    hue = gauss(mu, sigma)
    c = [hue%1,  light, sat]
    c = [int(255*val) for val in hls_to_rgb(*c)]
    return  Color(*c)

@app.setup()
def setup():
    global on, count, saturation, light, colors
    on = False
    count = 0

    #colorsys.hls_to_rgb(h, l, s)
    saturation = 0.7
    light = 0.3
    
    colors = [ randColor(light, saturation, mu=0) for _ in range(0, app.lamp.nb_pixel) ]

    
@app.every(0.05)
def loop():
    global on, count, saturation, light, colors

    #count += 1
    count = app.volume.value
    app.lamp.turn_on(flush=False)
    
    mu = (count / 900.) % 1
    # change one color:
    for _ in range(randint(0, 2)):
        k = randint(0, app.lamp.nb_pixel-1)
        colors[k] = randColor(light, saturation, mu=mu)
    
    for k in range(0, app.lamp.nb_pixel):
        app.lamp.turn_on(k+1, colors[k], flush=False)

    app.lamp.flush()

if __name__ == "__main__":
    app.run()

#-*- coding:utf-8 -*-
from __future__ import division
from lapp import LampApp

from ledpixels import Color

app = LampApp()

colorTop = None
ColorBot = None
i = None

@app.every(2)
def every():
    global colorTop, ColorBot, i
    colorTop = Color.random()
    ColorBot = Color.random()
    for i in range(1, 26):
        app.lamp.turn_on(i, Color.blend(colorTop, ColorBot, i / 24))


if __name__ == "__main__":
    app.run()
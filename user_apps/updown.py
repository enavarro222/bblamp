#-*- coding:utf-8 -*-
from __future__ import division

from lampapp import LampApp
from lampapp.ledpixels import Color

couleur = None
i = None

app = LampApp()

@app.setup()
def setup():
    pass

@app.every(1)
def every():
    global couleur, i
    couleur = Color.random()
    for i in range(1, 26):
        app.lamp.turn_on(i, couleur)
        if i > 1:
            app.lamp.turn_off(i - 1)
        app.wait((70) / 1000.)
    for i in range(24, 0, -1):
        app.lamp.turn_on(i, couleur)
        app.lamp.turn_off(i + 1)
        app.wait((70) / 1000.)


if __name__ == "__main__":
    app.run()
#-*- coding:utf-8 -*-
from __future__ import division
from lampapp import LampApp

from lampapp.ledpixels import Color
from lampapp.wiimote import BTN_A

app = LampApp()
app.activate_wiimote()

couleur = None
i = None

@app.setup()
def setup():
    global couleur
    couleur = Color(255, 0, 0)

@app.every(1)
def every():
    global couleur, i
    for i in range(1, 26):
        app.lamp.turn_on(i, couleur)
        if i > 1:
            app.lamp.turn_off(i - 1)
        app.wait((70) / 1000.)
    for i in range(24, 0, -1):
        app.lamp.turn_on(i, couleur)
        app.lamp.turn_off(i + 1)
        app.wait((70) / 1000.)

@app.wiimote.pressed(BTN_A)
def pressed_a():
    global couleur
    couleur = Color(0, 255, 0)


@app.wiimote.released(BTN_A)
def released_a():
    global couleur
    couleur = Color(255, 0, 0)

if __name__ == "__main__":
    app.run()

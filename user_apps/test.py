#-*- coding:utf-8 -*-
from __future__ import division
from lampapp import LampApp

from lampapp.ledpixels import Color
from lampapp.wiimote import BTN_UP, BTN_DOWN

app = LampApp()
app.need("wiimote")
app.wiimote.enable_acc()

i = 1

@app.wiimote.pressed(BTN_UP)
def up():
    global i
    i = min(32, i+1)

@app.wiimote.pressed(BTN_DOWN)
def down():
    global i
    i = max(1, i-1)

@app.setup()
def setup():
    global couleur
    couleur = Color(255, 0, 0)

@app.every(0.1)
def every():
    global couleur, i
    app.lamp.turn_off()
    app.lamp.turn_on(i, color=couleur)


if __name__ == "__main__":
    app.run()

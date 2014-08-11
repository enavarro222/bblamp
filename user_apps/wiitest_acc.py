#-*- coding:utf-8 -*-
from __future__ import division
from lampapp import LampApp

from lampapp.ledpixels import Color
from lampapp.wiimote import BTN_A

app = LampApp()
app.activate_wiimote()
app.wiimote.enable_acc()

couleur = None
i = None

def acc_to_color():
    acc = [app.wiimote.get_acc_x(), app.wiimote.get_acc_y(), app.wiimote.get_acc_z()]
    acc = [min(255, max(0, (val-90)*3)) for val in acc]
    return Color(*acc)

@app.setup()
def setup():
    global couleur
    couleur = Color(255, 0, 0)

@app.every(0.1)
def every():
    global couleur, i
    couleur = acc_to_color()
    app.lamp.turn_on(color=couleur)
    #for i in range(1, 26):
    #    app.lamp.turn_on(i, couleur)


if __name__ == "__main__":
    app.run()

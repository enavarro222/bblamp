#-*- coding:utf-8 -*-
from __future__ import division

from lampapp import LampApp
from lampapp.ledpixels import Color

app = LampApp()

@app.setup()
def setup():
    app.lamp.turn_on(20, Color.from_html('#009900'))
    app.lamp.turn_on(18, Color.from_html('#cc0000'))


if __name__ == "__main__":
    app.run()
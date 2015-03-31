#-*- coding:utf-8 -*-
from lampapp import LampApp
from hardware.lamp import Color #FIXME odd import..

app = LampApp()
app.need("lamp")

@app.setup()
def setup():
    app.lamp.turn_on(20, Color.from_html('#009900'))
    app.lamp.turn_on(18, Color.from_html('#cc0000'))


on = True

@app.every(1)
def loop():
    global on
    if on:
        app.lamp.turn_off(18)
    else:
        app.lamp.turn_on(18, Color.from_html('#cc0000'))
    on = not on
    
if __name__ == "__main__":
    app.run()

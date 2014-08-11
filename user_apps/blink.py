#-*- coding:utf-8 -*-
from lampapp import LampApp
from hardware.lamp import Color #FIXME odd import..

app = LampApp()
app.need("lamp")
app.need("gauge")
app.need("bp_rouge")
app.need("sw_band")
app.need("volume")

# variables
color_off = None
color_on = None
volume = None

@app.setup()
def setup():
    global color_on
    global color_off
    global volume

    update_and_draw()

    while True:
        app.wait(1)

@app.bp_rouge.change()
def bp_route_changed():
    update_and_draw()

@app.sw_band.change()
def sw_band_changed():
    update_and_draw()

@app.volume.change()
def volume_changed():
    update_and_draw()

def update_and_draw():
    global color_on
    global color_off
    global volume

    volume = app.volume.value
    app.gauge.value = volume

    if app.sw_band.value:
        color_off = Color(40, 40, 40)
    else:
        color_off = None

    if app.bp_rouge.value:
        color_on = Color(255, 20, 20)
    else:
        color_on = Color(10, 220, 100)


    nb_on = max(1, (app.lamp.nb_pixel * volume) / 845)
    print color_on, color_off, volume, nb_on

    #set colors
    for led in range(1, nb_on):
        if color_on is not None:
            app.lamp.set_color(led, color_on)
    for led in range(app.lamp.nb_pixel, nb_on-1, -1):
        if color_off is not None:
            app.lamp.set_color(led, color_off)

    for led in range(1, nb_on):
        app.lamp.on(led)
    for led in range(app.lamp.nb_pixel, nb_on-1, -1):
        if color_off is not None:
            app.lamp.on(led)
        else:
            app.lamp.off(led)
    app.lamp.flush()


if __name__ == "__main__":
    app.run()

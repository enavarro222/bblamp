#-*- coding:utf-8 -*-
from lapp import LampApp

app = LampApp()

@app.setup()
def setup():
    global on, count
    on = False
    count = 0

@app.every(1)
def loop():
    global on, count
    # msg every 10 blink
    if count % 10 == 0:
        app.msg("still a live !")
    if count % 30 == 10:
        app.log.info("Log test !")
    count += 1
    # blink
    if on:
        app.lamp.turn_off()
    else:
        app.lamp.turn_on()
    on = not on

if __name__ == "__main__":
    app.run()

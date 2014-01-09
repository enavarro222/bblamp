#-*- coding:utf-8 -*-
from lapp import LampApp
from ledpixels import Color

app = LampApp()

@app.setup()
def setup():
    global on, count, position, sens, period, colors
    
    on = False
    count = 0
    position = [1, 20, 6, 15]
    sens = [1, -1, 1, -1]
    period = [14, 6, 25, 60]
    
    colors = [
        Color(202,  12, 105),
        Color(250,  200, 12),
        Color(12,  248, 15),
        Color(12,  127, 100),
    ]
    
@app.every(0.01)
def loop():
    global on, count, position, sens, period, colors
    # msg every 10 blink
    
    count += 1
    app.lamp.off()

    for k in range( len( position ) ):
        app.lamp.turn_on(position[k], colors[k], flush=False)

        # mouv:
        if count % period[k] == 0:
            if position[k] == 1:
                sens[k] = 1
            elif position[k] == 24:
                sens[k] = -1
            position[k] += sens[k]    

    app.lamp.flush()    

if __name__ == "__main__":
    app.run()
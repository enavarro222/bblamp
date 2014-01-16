#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import time

from ledpixels import LedPixels

rose = (255, 50, 50)
vert = (60, 204, 10)

npixels = 25
traine = 4

def borne(val):
    val = max(val, 0)
    val = min(val, npixels)
    return val
# x x x x x x x
# T Q Q
def pixels(pos, traine, direction):
    tete = borne(pos)
    if direction:
        queue = range(borne(tete-traine), tete)
    else:
        queue = range(tete+1, borne(tete+traine+1))
    return tete, queue

def main():
    lamp = LedPixels(npixels)
    lamp.all_off()
    lamp.flush()
    pos = 0
    direction = True
    for _ in range(90*26):
        pos += 1 if direction else -1
        pos %= npixels
        if direction and pos == npixels - 1:
            print("change direction")
            direction = not direction
            pos = npixels - traine
        if not direction and pos == 0:
            print("change direction")
            direction = not direction
            pos = traine
        lamp.all_off()
        tete, queue = pixels(pos, traine, direction)
        lamp.set_color(tete, *rose)
        lamp.switch_on(tete)
        for val in queue:
            lamp.set_color(val, *vert)
            lamp.switch_on(val)
        lamp.flush()
        time.sleep(0.05)
    
    lamp.set_color_all(255, 50, 50)
    lamp.all_on()
    lamp.flush()

    return 0

if __name__ == '__main__':
    sys.exit(main())


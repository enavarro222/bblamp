#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import time

from ledpixels import LedPixels


def main():
    npixels = 25
    lamp = LedPixels(npixels)
    lamp.all_off()
    lamp.flush()
    lnum = 0
    for _ in range(26):
        lamp.switch_off(lnum)
        lnum = (lnum + 1) % npixels
        lamp.switch_on(lnum)
        lamp.flush()
        time.sleep(0.1)
    
    lamp.set_color_all(255, 50, 50)
    lamp.all_on()
    lamp.flush()

    return 0

if __name__ == '__main__':
    sys.exit(main())


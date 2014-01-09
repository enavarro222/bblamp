#-*- coding:utf-8 -*-
import random

import array
import fcntl

import requests
import json


class Color(object):
    """ Color object, internal representation is 3 octets for rgb
    """
    @staticmethod
    def from_html(colorstring):
        """ Create a color from RGB value given in HTML format '#RRGGBB'
        """
        colorstring = colorstring.strip()
        if colorstring[0] == '#':
            colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return Color(r, g, b)

    @staticmethod
    def from_rgb100(r, g, b):
        """ Create a color from RGB value given between 0 and 1OO
        """
        r, g, b = [round(n*2.55) for n in (r, g, b)]
        return Color(r, g, b)

    @staticmethod
    def random():
        return Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @staticmethod
    def blend(color_l, color_r, ratio=0.5):
        """ Blend two colours together
        """
        ratio = min(1, max(0, ratio))
        color = Color()
        color.r = round(color_l.r * (1 - ratio) + color_r.r * ratio)
        color.g = round(color_l.g * (1 - ratio) + color_r.g * ratio)
        color.b = round(color_l.b * (1 - ratio) + color_r.b * ratio)
        return color

    def __init__(self, r=0, g=0, b=0):
        self._rgb = bytearray(3)
        self.r = r
        self.g = g
        self.b = b
    
    def html(self):
        return '#%02x%02x%02x' % self.rgb_int

    def __str__(self):
        return self.html()

    def __repr__(self):
        return self.html()

    def _set(self, cid, val):
        self._rgb[cid] = min(255, max(0, int(round(val))))
    
    @property
    def rgb_bytearray(self):
        return self._rgb

    @property
    def rgb_int(self):
        return tuple(int(val) for val in self.rgb_bytearray)

    @property
    def r(self):
        return self._rgb[0]

    @r.setter
    def r(self, r):
        self._set(0, r)

    @property
    def g(self):
        return self._rgb[1]

    @g.setter
    def g(self, g):
        self._set(1, g)

    @property
    def b(self):
        return self._rgb[2]

    @b.setter
    def b(self, b):
        self._set(2, b)

BLACK = Color.from_html("#000000")
WHITE = Color.from_html("#FFFFFF")


class LedPixelsAbstract():
    def __init__(self, nb_pixel=25):
        self._nb_pixel = nb_pixel
        self.colors = [Color() for _ in xrange(self._nb_pixel)]
        self.set_color_all(Color(255, 100, 0))
        self.is_on = [True for _ in xrange(self._nb_pixel)]

    def flush(self):
        raise NotImplementedError()

    def set_color(self, lnum, color):
        assert 1 <= lnum <= self._nb_pixel
        self.colors[lnum-1] = color

    def set_color_all(self, color):
        for lnum in xrange(1, self._nb_pixel+1):
            self.set_color(lnum, color)

    def on(self, lnum=None):
        if lnum is None:
            self.is_on = [True] * self._nb_pixel
        else:
            assert 1 <= lnum <= self._nb_pixel
            self.is_on[lnum-1] = True

    def off(self, lnum=None):
        if lnum is None:
            self.is_on = [False] * self._nb_pixel
        else:
            assert 1 <= lnum <= self._nb_pixel
            self.is_on[lnum-1] = False

    def turn_on(self, lnum=None, color=None, flush=True):
        if color is not None:
            if lnum is None:
                self.set_color_all(color)
            else:
                self.set_color(lnum, color)
        self.on(lnum)
        if flush:
            self.flush()

    def turn_off(self, lnum=None, flush=True):
        self.off(lnum)
        if flush:
            self.flush()

class LedPixels(LedPixelsAbstract):
    """ The WS2801 led string on rPy
    """
    def __init__(self, nb_pixel=25):
        LedPixelsAbstract.__init__(self, nb_pixel)
        self._spidev = file("/dev/spidev0.0", "wb")
        fcntl.ioctl(self._spidev, 0x40046b04, array.array('L', [400000]))

    def flush(self):
        for lnum, color in enumerate(self.colors):
            if self.is_on[lnum]:
                self._spidev.write(color.rgb_bytearray)
            else:
                self._spidev.write(BLACK.rgb_bytearray)
        self._spidev.flush()


class LedPixelsWebSimu(LedPixelsAbstract):
    def __init__(self, nb_pixel=25):
        LedPixelsAbstract.__init__(self, nb_pixel)
        self._leds_url = "http://localhost:5000/simu/v1/leds"

    def flush(self):
        colors = []
        for lnum, color in enumerate(self.colors):
            if self.is_on[lnum]:
                colors.append(color.rgb_int)
            else:
                colors.append(BLACK.rgb_int)
        json_data = json.dumps(colors)
        headers = {'Content-Type': 'application/json'}
        requests.put(self._leds_url, data=json_data, headers=headers)


class LedPixelsFileStub(LedPixelsAbstract):
    def __init__(self, nb_pixel=25):
        LedPixelsAbstract.__init__(self, nb_pixel)
        self._output_filename = "LedPixels"

    def flush(self):
        with file("lapp_output/ledpixels", "w") as _spidev:
            for lnum, color in enumerate(self.colors):
                if self.is_on[lnum]:
                    _spidev.write("%i %i %i" % color.rgb_int)
                else:
                    _spidev.write("%i %i %i" % BLACK.rgb_int)
                _spidev.write("\n")


#-*- coding:utf-8 -*-
import random

import array
import fcntl

import requests
import json

from hardware import BBLampHardware

# --- 
class Color(object):
    """ Color object, internal representation is 3 octets for rgb
    """
    
    # Gamma correction compensates for our eyes' nonlinear perception of
    # intensity.  It's the LAST step before a pixel value is stored, and
    # allows intermediate rendering/processing to occur in linear space.
    # The table contains 256 elements (8 bit input), though the outputs are
    # only 7 bits (0 to 127).  This is normal and intentional by design: it
    # allows all the rendering code to operate in the more familiar unsigned
    # 8-bit colorspace (used in a lot of existing graphics code), and better
    # preserves accuracy where repeated color blending operations occur.
    # Only the final end product is converted to 7 bits, the native format
    # for the LPD8806 LED driver.  Gamma correction and 7-bit decimation
    # thus occur in a single operation.
    gammaTable  = [
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
        1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,
        2,  2,  2,  2,  2,  3,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,
        4,  4,  4,  4,  5,  5,  5,  5,  5,  6,  6,  6,  6,  6,  7,  7,
        7,  7,  7,  8,  8,  8,  8,  9,  9,  9,  9, 10, 10, 10, 10, 11,
       11, 11, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 15, 15, 16, 16,
       16, 17, 17, 17, 18, 18, 18, 19, 19, 20, 20, 21, 21, 21, 22, 22,
       23, 23, 24, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 29, 29, 30,
       30, 31, 32, 32, 33, 33, 34, 34, 35, 35, 36, 37, 37, 38, 38, 39,
       40, 40, 41, 41, 42, 43, 43, 44, 45, 45, 46, 47, 47, 48, 49, 50,
       50, 51, 52, 52, 53, 54, 55, 55, 56, 57, 58, 58, 59, 60, 61, 62,
       62, 63, 64, 65, 66, 67, 67, 68, 69, 70, 71, 72, 73, 74, 74, 75,
       76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91,
       92, 93, 94, 95, 96, 97, 98, 99,100,101,102,104,105,106,107,108,
      109,110,111,113,114,115,116,117,118,120,121,122,123,125,126,127
    ];
    
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
        return str(self)

    def _set(self, cid, val):
        self._rgb[cid] = min(255, max(0, int(round(val))))
    
    @property
    def rgb_bytearray(self):
        return self._rgb

    @property
    def rgb_bytearray_gamma(self):
        _rgb_gamma = bytearray(3)
        for i in range(3):
            _rgb_gamma[i] = Color.gammaTable[self.rgb_bytearray[i]] << 1
        return _rgb_gamma

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

# -----------------------------------------------------------------------------

class LedPixelsAbstract(BBLampHardware):
    def __init__(self, nb_pixel=25):
        super(LedPixelsAbstract, self).__init__()
        self._nb_pixel = nb_pixel
        self.colors = [Color() for _ in xrange(self.nb_pixel)]
        self.set_color_all(Color(255, 100, 0))
        self.is_on = [True for _ in xrange(self.nb_pixel)]

    def activate(self, app):
        self.off()

    def exit(self, app):
        self.off()

    @property
    def nb_pixel(self):
        return self._nb_pixel

    def flush(self):
        raise NotImplementedError()

    def set_color(self, lnum, color):
        assert 1 <= lnum <= self.nb_pixel, "'%s' is not a valid led number" % lnum
        self.colors[lnum-1] = color

    def set_color_all(self, color):
        for lnum in xrange(1, self.nb_pixel+1):
            self.set_color(lnum, color)

    def get_color(self, lnum):
        if self.is_on[lnum-1]:
            return self.colors[lnum-1]
        else:
            return BLACK

    def on(self, lnum=None):
        if lnum is None:
            self.is_on = [True] * self.nb_pixel
        else:
            assert 1 <= lnum <= self.nb_pixel, "'%s' is not a valid led number" % lnum
            self.is_on[lnum-1] = True

    def off(self, lnum=None):
        if lnum is None:
            self.is_on = [False] * self.nb_pixel
        else:
            assert 1 <= lnum <= self.nb_pixel, "'%s' is not a valid led number" % lnum
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
        for lnum in range(1, self.nb_pixel+1):
            color = self.get_color(lnum)
            self._spidev.write(color.rgb_bytearray_gamma)
        self._spidev.flush()


class LedPixelsWebSimu(LedPixelsAbstract):
    def __init__(self, nb_pixel=25):
        LedPixelsAbstract.__init__(self, nb_pixel)
        self._leds_url = "http://localhost:5000/simu/v1/leds"

    def flush(self):
        colors = []
        for lnum in range(1, self.nb_pixel+1):
            color = self.get_color(lnum)
            colors.append(color.rgb_int)
        json_data = json.dumps(colors)
        headers = {'Content-Type': 'application/json'}
        requests.put(self._leds_url, data=json_data, headers=headers)


class LedPixelsFileStub(LedPixelsAbstract):
    def __init__(self, nb_pixel=25):
        LedPixelsAbstract.__init__(self, nb_pixel)
        self._output_filename = "LedPixels"

    def flush(self):
        with file("lapp_output/ledpixels", "w") as _spidev:
            for lnum in range(1, self.nb_pixel+1):
                color = self.get_color(lnum)
                _spidev.write("%i %i %i" % color.rgb_int)
                _spidev.write("\n")


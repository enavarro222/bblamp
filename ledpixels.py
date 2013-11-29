#-*- coding:utf-8 -*-

import array
import fcntl

class LedPixels():
    def __init__(self, nb_pixel=25):
        self._spidev = file("/dev/spidev0.0", "wb")
        fcntl.ioctl(self._spidev, 0x40046b04, array.array('L', [400000]))
        self._nb_pixel = nb_pixel
        self.colors = [bytearray(3) for _ in xrange(self._nb_pixel)]
        self.set_color_all(255, 100, 0)
        self.is_on = [True for _ in xrange(self._nb_pixel)]

    def flush(self):
        for lnum, rgb in enumerate(self.colors):
            if self.is_on[lnum]:
                self._spidev.write(rgb)
            else:
                black = bytearray(3)
                black[0] = black[1] = black[2] = 0
                self._spidev.write(black)
        self._spidev.flush()

    def set_color(self, lnum, r, g, b):
        assert 0 <= lnum < self._nb_pixel
        rgb = self.colors[lnum]
        rgb[0] = r
        rgb[1] = g
        rgb[2] = b

    def set_color_all(self, r, g, b):
        for lnum in xrange(self._nb_pixel):
            self.set_color(lnum, r, g, b)

    def all_off(self):
        for lnum in xrange(self._nb_pixel):
            self.switch_off(lnum)

    def all_on(self):
        for lnum in xrange(self._nb_pixel):
            self.switch_on(lnum)

    def switch_on(self, lnum):
        assert 0 <= lnum < self._nb_pixel
        self.is_on[lnum] = True

    def switch_off(self, lnum):
        assert 0 <= lnum < self._nb_pixel
        self.is_on[lnum] = False


class LedPixelsFileStub():
    def __init__(self, nb_pixel=25):
        self._output_filename = "LedPixels"
        self._nb_pixel = nb_pixel
        self.colors = [bytearray(3) for _ in xrange(self._nb_pixel)]
        self.set_color_all(255, 100, 0)
        self.is_on = [True for _ in xrange(self._nb_pixel)]

    def flush(self):
        with file("lapp_output/ledpixels", "w") as _spidev:
            for lnum, rgb in enumerate(self.colors):
                if self.is_on[lnum]:
                    _spidev.write("%i %i %i" % (rgb[0], rgb[1], rgb[2]))
                else:
                    black = bytearray(3)
                    black[0] = black[1] = black[2] = 0
                    _spidev.write("%i %i %i" % (black[0], black[1], black[2]))
                _spidev.write("\n")

    def set_color(self, lnum, r, g, b):
        rgb = self.colors[lnum]
        rgb[0] = r
        rgb[1] = g
        rgb[2] = b

    def set_color_all(self, r, g, b):
        for lnum in xrange(self._nb_pixel):
            self.set_color(lnum, r, g, b)

    def all_off(self):
        for lnum in xrange(self._nb_pixel):
            self.switch_off(lnum)

    def all_on(self):
        for lnum in xrange(self._nb_pixel):
            self.switch_on(lnum)

    def switch_on(self, lnum):
        assert 0 <= lnum < self._nb_pixel
        self.is_on[lnum] = True

    def switch_off(self, lnum):
        assert 0 <= lnum < self._nb_pixel
        self.is_on[lnum] = False


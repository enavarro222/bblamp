#!/usr/bin/env python
#-*- coding:utf-8 -*-


class BBLampHardware(object):
    default_attr_name = None

    def __init__(self):
        pass

    def activate(self, app):
        pass

    def exit(self, app):
        pass


import struct

# some i2c helper
#class I2CBus(object):
class I2CBus(object):
    def __init__(self, i2c_slave, i2c_bus=0):
        import smbus
        self._bus = smbus.SMBus(i2c_bus)
        self._i2c_slave = i2c_slave
        #TODO: check i2c device exist

    def _read_i2c(self, cmd, nb_bytes=4, cast="f"):
        """
        to see all possible cast:
        http://docs.python.org/2/library/struct.html#format-characters
        """
        nb_err = 0
        ok = False
        while not ok:
            try:
                bytes = self._bus.read_i2c_block_data(self._i2c_slave, cmd, nb_bytes)
            except IOError:
                if nb_err >= 5:
                    raise
                nb_err += 1
            else:
                ok = True
        return struct.unpack(cast, "".join(map(chr, bytes)))[0]

    def _write_i2c(self, cmd, bytes):
        self._bus.write_i2c_block_data(self._i2c_slave, cmd, bytes)

    def read_float(self, cmd):
        return self._read_i2c(cmd, 4, "f")

    def read_long(self, cmd):
        return self._read_i2c(cmd, 4, "l")

    def read_unsigned_long(self, cmd):
        return self._read_i2c(cmd, 4, "l")

    def write_long(self, cmd, value):
        bytes = [value >> i & 0xff for i in range(24, -1, -8)]
        bytes.reverse()
        self._write_i2c(cmd, bytes)


class I2CBusPigpio(I2CBus):

    def __init__(self, pi, i2c_slave, i2c_bus=0):
        super(I2CBusPigpio, self).__init__(i2c_slave, i2c_bus=i2c_bus)
        self.pi = pi
        self.slave = self.pi.i2c_open(i2c_bus, i2c_slave)
        self._i2c_slave = i2c_slave

    def _read_i2c(self, cmd, nb_bytes=4, cast="f"):
        """
        to see all possible cast:
        http://docs.python.org/2/library/struct.html#format-characters
        """
        nb, bytes = self.pi.i2c_read_i2c_block_data(self.slave, cmd, nb_bytes)
        if nb < 0:
            raise IOError
        bytes = str(bytes)
        return struct.unpack(cast, bytes)[0]

    def _write_i2c(self, cmd, bytes):
        self.pi.i2c_write_i2c_block_data(self.slave, cmd, bytes)



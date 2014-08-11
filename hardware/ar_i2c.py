#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time

import pigpio

from hardware import BBLampHardware
from hardware import I2CBus

class ArI2C(object):
    instance = None

    def __init__(self):
        if ArI2C.instance is not None:
            raise RuntimeError("Only one instance of ArI2C may exist, use get_instance() instead")
        ArI2C.instance = self
        self.slave_addr = 0x28
        self.irq_pin = 22
        self.bus = None
        self.pi = None
        self.callbacks = {}
        self.activate()

    @staticmethod
    def get_instance():
        if ArI2C.instance is None:
            return ArI2C()
        return ArI2C.instance

    def activate(self):
        self.pi = pigpio.pi()
        #self.bus = I2CBusPigpio(self.pi, 0x28, i2c_bus=1)
        self.bus = I2CBus(self.slave_addr, i2c_bus=1)
        # arduino IRQ
        self.pi.callback(self.irq_pin, pigpio.FALLING_EDGE, self._callback)

    def register_callback(self, mask, callback):
        if mask in self.callbacks:
            raise ValueError("mask %d already present" % mask)
        self.callbacks[mask] = callback

    def _callback(self, gpio, level, tick):
        # read what changed
        what_changed = self.bus.read_long(0x00)
        # check for all registered if mask match, then callback
        for mask, callback in self.callbacks.iteritems():
            if what_changed & mask:
                callback()

    def read_float(self, cmd):
        return self.bus.read_float(cmd)

    def read_long(self, cmd):
        return self.bus.read_long(cmd)

    def read_unsigned_long(self, cmd):
        return self.bus.read_unsigned_long(cmd)

    def write_long(self, cmd, value):
        self.bus.write_long(cmd, value)


class ArGauge(BBLampHardware):
    def __init__(self):
        super(ArGauge, self).__init__()
        #self.pi = pigpio.pi()
        #self.bus = I2CBusPigpio(self.pi, 0x28, i2c_bus=1)
        self.bus = I2CBus(0x28, i2c_bus=1)
        self._value = None;

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        if val != self._value:
            assert 0 <= val <= 932, "Invalid value : %d" % val
            self.bus.write_long(0xC0, val)
            self._value = val

class ArI2CIntSensor(BBLampHardware):
    def __init__(self, sensor_id, ari2c=None):
        super(ArI2CIntSensor, self).__init__()
        self.sensor_id = sensor_id
        self.ari2c = None
        self._user_ari2c = ari2c
        self._on = []

    def activate(self, lamp):
        self.ari2c = self._user_ari2c
        if self.ari2c is None:
            self.ari2c = ArI2C.get_instance()
        self.ari2c.register_callback(self.sensor_id, self._changed)

    @property
    def value(self):
        if self.ari2c is None:
            raise RuntimeError("This should be activated first !")
        return self.ari2c.read_long(self.sensor_id)

    def on(self, fct):
        self._on.append(fct)

    def change(self):
        """ decorator that declare a callback
        """
        def change_deco(fn):
            self.on(fn)
            return fn
        return change_deco

    def _changed(self):
        #print("%s Changed !" % self.sensor_id)
        for fct in self._on:
            fct()


class ArBpRouge(ArI2CIntSensor):
    def __init__(self, ari2c=None):
        super(ArBpRouge, self).__init__(0x01, ari2c=ari2c)

    @property
    def value(self):
        return not super(ArBpRouge, self).value

class ArSwBand(ArI2CIntSensor):
    def __init__(self, ari2c=None):
        super(ArSwBand, self).__init__(0x02, ari2c=ari2c)

    @property
    def value(self):
        return not super(ArSwBand, self).value

class ArSwFct(ArI2CIntSensor):
    def __init__(self, ari2c=None):
        super(ArSwFct, self).__init__(0x04, ari2c=ari2c)

class ArVolume(ArI2CIntSensor):
    def __init__(self, ari2c=None):
        super(ArVolume, self).__init__(0x10, ari2c=ari2c)
    #TODO add config du diff pour callback

    @property
    def value(self):
        return max(0, min(super(ArVolume, self).value, 845))

#TODO more generic hardware: btn, switch, pot
class ArBoutons(BBLampHardware):
    def __init__(self):
        super(ArBoutons, self).__init__()
        self.pi = pigpio.pi()
        #self.bus = I2CBusPigpio(self.pi, 0x28, i2c_bus=1)
        self.bus = I2CBus(0x28, i2c_bus=1)
        self.irq_pin = 22
        self._bp_rouge = self.bp_rouge
        # callback
        self.pi.set_mode(self.irq_pin, pigpio.INPUT)
        self.cb1 = self.pi.callback(self.irq_pin, pigpio.FALLING_EDGE, self._callback)

    @property
    def bp_rouge(self):
        return not self.bus.read_long(0xB0)

    @property
    def sw_band(self):
        return self.bus.read_long(0xB1)

    @property
    def sw_fct(self):
        return self.bus.read_long(0xB2)

    @property
    def volume(self):
        """Return a value between 0 and 845"""
        val = self.bus.read_long(0xA0)
        return max(0, min(val, 845))

    def _callback(self, gpio, level, tick):
        print("Callback !")
        print(gpio, level, tick)


###################
def test_i2c():
    bus = smbus.SMBus(1)
    bus.write_i2c_block_data(0x28, 0xC0, [20,1])
    time.sleep(1)
    bus.write_i2c_block_data(0x28, 0xC0, [20,3])
    time.sleep(1)
    temp = struct.unpack("f", "".join(map(chr, bus.read_i2c_block_data(0x28, 0x21, 4))))
    print("temp: %1.2f°C" % temp)


def main():
    gauge = ArGauge()
    btns = ArBoutons()

    gauge.value = 0
    time.sleep(1)
    gauge.value = 800
    time.sleep(2)
    for i in range(0,1000,100):
        print i
        gauge.value = i
        print(btns.bp_rouge)
        time.sleep(1)

#    def cbf(gpio, level, tick):
#        print("Callback !")
#        print(btns.bp_rouge)
#        print(gpio, level, tick)

#    pi = pigpio.pi()
#    irq_pin = 22
#    pi.set_mode(irq_pin, pigpio.INPUT)
#    cb1 = pi.callback(irq_pin, pigpio.EITHER_EDGE, cbf)

    while True:
        #print(pi.read(irq_pin))
        time.sleep(0.01)
    pi.stop()



if __name__ == '__main__':
    import sys
    sys.exit(main())



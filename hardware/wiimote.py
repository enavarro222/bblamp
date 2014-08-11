#-*- coding:utf-8 -*-
import cwiid

# btn cst
from cwiid import BTN_2, BTN_1, BTN_B, BTN_A, \
    BTN_MINUS, BTN_HOME, BTN_PLUS, \
    BTN_LEFT, BTN_RIGHT, BTN_DOWN, BTN_UP

from hardware import BBLampHardware

PRESSED = 1
RELEASED = 2

class WiimoteError(RuntimeError):
    pass

class Wiimote(BBLampHardware):

    BTNS = [
        (cwiid.BTN_2, "2"),           # 1
        (cwiid.BTN_1, "1"),           # 2
        (cwiid.BTN_B, "B"),           # 4
        (cwiid.BTN_A, "A"),           # 8
        (cwiid.BTN_MINUS, "MINUS"),   # 16
        (cwiid.BTN_HOME, "HOME"),     # 128
        (cwiid.BTN_LEFT, "LEFT"),     # 256
        (cwiid.BTN_RIGHT, "RIGHT"),   # 512
        (cwiid.BTN_DOWN, "DOWN"),     # 1024
        (cwiid.BTN_UP, "UP"),         # 2048
        (cwiid.BTN_PLUS, "PLUS"),     # 4096
    ]

    def __init__(self):
        super(BBLampHardware, self).__init__()
        self._connected = False
        self._wm = None
        self._led = 0
        self._rpt_mode = cwiid.RPT_BTN # by default read only btns
        self._last_btn = 0
        # init callbacks
        self._on = {} # self._on[BTN][PRESSED]

    def activate(self):
        self.connect()

    def connect(self):
        #TODO: add msg throw log ?
        try:
            self._wm = cwiid.Wiimote()
            self._wm.mesg_callback = self._callback
            # enable callbacks and (re)set wiimote set
            self._wm.enable(cwiid.FLAG_MESG_IFC)
            self._wm.rpt_mode = self._rpt_mode
            self._wm.led = self._led
            self._connected = True
        except RuntimeError, ValueError:
            # connection fail
            raise WiimoteError()

    def connected(self):
        return self._connected

    def close(self):
        self._connected = False
        if self._wm is not None:
            self._wm.close()
            self._wm = None

    def enable_acc(self):
        """ enable accelerometer read
        """
        self._rpt_mode |= cwiid.RPT_ACC
        try:
            self._wm.rpt_mode = self._rpt_mode
        except AttributeError:
            self.close()

    def get_acc_x(self):
        state = self._wm.state
        if "acc" in state:
            return state["acc"][cwiid.X]

    def get_acc_y(self):
        state = self._wm.state
        if "acc" in state:
            return state["acc"][cwiid.Z]

    def get_acc_z(self):
        state = self._wm.state
        if "acc" in state:
            return state["acc"][cwiid.Y]

    def led_on(self, lid):
        assert 0 <= lid < 4
        self._led |= 2**lid
        try:
            self._wm.led = self._led
        except AttributeError:
            self.close()

    def led_off(self, lid):
        assert 0 <= lid < 4
        self._led &= ~2**lid
        try:
            self._wm.led = self._led
        except AttributeError:
            self.close()

    def rumble_on(self):
        try:
            self._wm.rumble = 1
        except AttributeError:
            self.close()

    def rumble_off(self):
        try:
            self._wm.rumble = 0
        except AttributeError:
            self.close()

    def is_pressed(self, btn):
        btns = self._wm.state["buttons"]
        return btns & btn > 0

    def _callback(self, mesg_list, time):
        """ Wimote action callback function
        """
        for mesg in mesg_list:
            if mesg[0] == cwiid.MESG_ACC:
                continue
                #print 'Acc Report: x=%d, y=%d, z=%d' % \
                #      (mesg[1][cwiid.X], mesg[1][cwiid.Y], mesg[1][cwiid.Z])
            elif mesg[0] == cwiid.MESG_BTN:
                btn = mesg[1]
                # what changed ?
                changed = btn ^ self._last_btn
                for btn_mask, actions in self._on.iteritems():
                    if btn_mask & changed:
                        if PRESSED in actions and btn_mask & btn:
                            for callback in actions[PRESSED]:
                                callback()
                        elif RELEASED in actions:
                            for callback in actions[RELEASED]:
                                callback()
                self._last_btn = btn
            elif mesg[0] ==  cwiid.MESG_ERROR:
                #"Error message received"
                self.close()
            else:
                print 'Unknown Report'
            pass
    
    def on(self, btn, action, callback):
        """ Define an action on a callback
        """
        if not btn in self._on:
            self._on[btn] = {}
        if not action in self._on[btn]:
            self._on[btn][action] = []
        self._on[btn][action].append(callback)

    def pressed(self, btn):
        """ decorator that declare a callback when a button is pressed
        """
        def pressed_deco(fn):
            self.on(btn, PRESSED, fn)
            return fn
        return pressed_deco

    def released(self, btn):
        """ decorator that declare a callback when a button is released
        """
        def released_deco(fn):
            self.on(btn, RELEASED, fn)
            return fn
        return released_deco


def main():
    wi = Wiimote()

    def cb_A():
        print("RELEASED A !")
    wi.on(BTN_A, RELEASED, cb_A)

    import time
    while True:
        # connect the wiimote
        if not wi.connected():
            try:
                print("connecting...")
                wi.connect()
                time.sleep(0.4)
                print("connected")
            except WiimoteError:
                print("connection fail")
                time.sleep(0.2)
        else:
            time.sleep(0.4)

    exit = False
    while not exit:
        c = sys.stdin.read(1)
        if c == "s":
            print wi._wm.state
        elif c == "a":
            print wi.is_pressed(BTN_A)
        exit = c == "x"
    wi.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())



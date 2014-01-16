#-*- coding:utf-8 -*-

import cwiid

class WiimoteError(RuntimeError):
    pass

class Wiimote():

    def __init__(self):
        self._wm = None
        self._led = 0
        self._rpt_mode = 0

    def connect(self):
        #TODO: add msg throw log ?
        try:
            self._wm = cwiid.Wiimote()
            self._wm.mesg_callback = self._callback
            # enable callbacks
            self._wm.disable(cwiid.FLAG_MESG_IFC)
        except RuntimeError:
            # connection fail
            raise WiimoteError()

    def enable_button(self):
        self._check()
        self._rpt_mode |= cwiid.RPT_BTN
        self._wm.rpt_mode = self._rpt_mode

    def disable_button(self):
        self._check()
        self._rpt_mode &= ~cwiid.RPT_BTN
        self._wm.rpt_mode = self._rpt_mode

    def _check(self):
        if self._wm is None:
            raise WiimoteError()
        try:
            self._wm.led = self._led
        except AttributeError:
            wiimote.close()
            raise WiimoteError()

    def led_on(self, lid):
        self._check()
        assert 0 <= lid < 4
        self._led |= 2**lid

    def led_off(self, lid):
        self._check()
        assert 0 <= lid < 4
        self._led &= ~2**lid

    def rumble_on(self):
        self._check()
        self._wm.rumble = 1

    def rumble_off(self):
        self._check()
        self._wm.rumble = 0

    def _callback(self, mesg, time):
        """ Wimote action callback function
        """
        print 'time: %f' % time
        for mesg in mesg_list:
            if mesg[0] == cwiid.MESG_ACC:
                continue
                #print 'Acc Report: x=%d, y=%d, z=%d' % \
                #      (mesg[1][cwiid.X], mesg[1][cwiid.Y], mesg[1][cwiid.Z])

            elif mesg[0] == cwiid.MESG_BTN:
                print 'Button Report: %.4X' % mesg[1]

#            elif mesg[0] == cwiid.MESG_STATUS:
#                print 'Status Report: battery=%d extension=' % \
#                       mesg[1]['battery'],
#                if mesg[1]['ext_type'] == cwiid.EXT_NONE:
#                    print 'none'
#                elif mesg[1]['ext_type'] == cwiid.EXT_NUNCHUK:
#                    print 'Nunchuk'
#                elif mesg[1]['ext_type'] == cwiid.EXT_CLASSIC:
#                    print 'Classic Controller'
#                elif mesg[1]['ext_type'] == cwiid.EXT_BALANCE:
#                    print 'Balance Board'
#                elif mesg[1]['ext_type'] == cwiid.EXT_MOTIONPLUS:
#                    print 'MotionPlus'
#                else:
#                    print 'Unknown Extension'

#            elif mesg[0] == cwiid.MESG_IR:
#                valid_src = False
#                print 'IR Report: ',
#                for src in mesg[1]:
#                    if src:
#                        valid_src = True
#                        print src['pos'],

#                if not valid_src:
#                    print 'no sources detected'
#                else:
#                    print

#            elif mesg[0] == cwiid.MESG_NUNCHUK:
#                print ('Nunchuk Report: btns=%.2X stick=%r ' + \
#                       'acc.x=%d acc.y=%d acc.z=%d') % \
#                      (mesg[1]['buttons'], mesg[1]['stick'],
#                       mesg[1]['acc'][cwiid.X], mesg[1]['acc'][cwiid.Y],
#                       mesg[1]['acc'][cwiid.Z])

#            elif mesg[0] == cwiid.MESG_CLASSIC:
#                print ('Classic Report: btns=%.4X l_stick=%r ' + \
#                       'r_stick=%r l=%d r=%d') % \
#                      (mesg[1]['buttons'], mesg[1]['l_stick'],
#                       mesg[1]['r_stick'], mesg[1]['l'], mesg[1]['r'])

#            elif mesg[0] ==  cwiid.MESG_BALANCE:
#                print ('Balance Report: right_top=%d right_bottom=%d ' + \
#                       'left_top=%d left_bottom=%d') % \
#                      (mesg[1]['right_top'], mesg[1]['right_bottom'],
#                       mesg[1]['left_top'], mesg[1]['left_bottom'])

#            elif mesg[0] == cwiid.MESG_MOTIONPLUS:
#                print 'MotionPlus Report: angle_rate=(%d,%d,%d)' % \
#                      mesg[1]['angle_rate']

            elif mesg[0] ==  cwiid.MESG_ERROR:
                #"Error message received"
                self._wm.close()
                raise WiimoteError()
            else:
                print 'Unknown Report'
            pass
    
    def on(self, action, callback):
        """ Define an action on a callback
        """
        pass


def main():
    

if __name__ == '__main__':
    sys.exit(main())



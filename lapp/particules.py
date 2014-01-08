#-*- coding:utf-8 -*-
import time

from lapp import LampApp

class MyLampApp(LampApp):

    def setup(self):
        self.on = False
        self.count = 0
        self.position = [6, 5, 7, 8, 4, 5, 10]
        self.sens = [1, 1, 1, -1, 1, 1, -1]
        self.period = [15, 15, 20, 40, 80, 20, 92]
        
        self.colors = [
            [202,  12, 105],
            [25,  2, 12],
            [12,  248, 15],
            [12,  12, 200],
            [140,  155, 15],
            [230,  12, 15],
            [12,  127, 100],
        ]
        
        self.nextMove = self.period
    
    def loop(self):
        # msg every 10 blink
        
        self.count += 1
        self.lamp.all_off()
        
        for k in range( len( self.position ) ):
            self.lamp.set_color(self.position[k], *self.colors[k])
            self.lamp.switch_on(self.position[k])
            
            # mouv:
            if self.count % self.period[k] == 0:
                
                if self.position[k] <= 0 or self.position[k] >= 24:
                    self.sens[k] = -self.sens[k]
                    
                self.position[k] = self.position[k] + self.sens[k]    
                

        self.lamp.flush()
        time.sleep(0.01)

if __name__ == "__main__":
    lapp = MyLampApp()
    lapp.run()
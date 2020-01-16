from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from GlobalVar import *

class CuelistThread(QThread):
    lampset = pyqtSignal(int, str, object)
    
    cur_pos = 0
    used_lamps = [1,243567]
    cuelist = {
        0: ["Test Cue 0", [1, 'Dimmer', 100], [2, 'Dimmer', 50]],
        1: ["Cue 1", [2, 'Dimmer', 100], [1, 'Dimmer', 50]],
        }
    
    def __init__(self):
        QThread.__init__(self)
        print("Started")
        
    def run(self):
        for lamp in self.used_lamps:
            try:
                nr_in_use[lamp] += 1
            except KeyError:
                error_log_global.append("CuelistThread: failed to find lamp nr {0:d}".format(lamp))
        
        loop = QEventLoop()
        loop.exec_()
        
    def __del__(self):
        print("Exiting")
    
    def _go(self, cue=-1):
        if cue == -1:
            cue = self.cur_pos + 1
        for lamp in self.cuelist[cue][1:]:
            self.lampset.emit(lamp[0], lamp[1], lamp[2])
    
    def _release(self):
        for lamp_num in self.used_lamps:
            try:
                nr_in_use[lamp_num] -= 1
                if nr_in_use[lamp_num] == 1:
                    self.lampset.emit(lamp_num, "Dimmer", 0)
            except KeyError:
                error_log_global.append("CuelistThread: failed to find lamp nr {0:d}".format(lamp_num))

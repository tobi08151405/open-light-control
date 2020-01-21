from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from GlobalVar import *

class CuelistThread(QThread):
    lampset = pyqtSignal(int, str, object)
    cuelist={}
    options={}

    cur_cue = 0
    # used_lamps = [1,243567]
    # cuelist = {
    #     0: ["Test Cue 0", [1, 'Dimmer', 100], [2, 'Dimmer', 50]],
    #     1: ["Cue 1", [2, 'Dimmer', 100], [1, 'Dimmer', 50]],
    #     }

    def __init__(self):
        QThread.__init__(self)
        print("Started")

    def set_cuelist(self, cuelist):
        try:
            self.cuelist = cuelist_dict[cuelist]
            self.options = self.cuelist.get("options", {})
        except KeyError:
            error_log_global.append("CuelistThread: cuelist {0:s} not defined".format(cuelist))

    def run(self):
        # for lamp in self.used_lamps:
        #     try:
        #         nr_in_use[lamp] += 1
        #     except KeyError:
        #         error_log_global.append("CuelistThread: failed to find lamp nr {0:d}".format(lamp))
        self.goto(min([x for x in self.cuelist.keys() if not isinstance(x, str)]))
        loop = QEventLoop()
        loop.exec_()

    def __del__(self):
        print("Exiting")

    def goto(self, cue):
        if cue == -1:
            cue = self.cur_cue + 1
        seq = [x for x in self.cuelist.keys() if not isinstance(x, str)]
        if cue == max(seq)+1 and self.options.get("warp_at_end", False):
            cue = min(seq)
        try:
            for lamp in self.cuelist.get(cue,self.cuelist[0])[1:]:
                self.lampset.emit(lamp[0], lamp[1], lamp[2])
        except KeyError:
            error_log_global.append("CuelistThread: cue {0:d} not defined".format(cue))
        self.cur_cue=cue

    def go(self):
        self.goto(-1)

    def release(self):
        for lamp_num in self.used_lamps:
            try:
                nr_in_use[lamp_num] -= 1
                if nr_in_use[lamp_num] == 1:
                    self.lampset.emit(lamp_num, "Dimmer", 0)
            except KeyError:
                error_log_global.append("CuelistThread: failed to find lamp nr {0:d}".format(lamp_num))

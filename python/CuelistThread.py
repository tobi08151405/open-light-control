from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from GlobalVar import *

from time import time
# import pdb

class CuelistThread(QThread):
    lampset = pyqtSignal(int, str, object)
    cuelist={}
    options={}

    fade = False
    cur_cue = 0
    next_cue = 0
    # used_lamps = [1,243567]
    # cuelist = {
    #     0: ["Test Cue 0", [1, 'Dimmer', 100], [2, 'Dimmer', 50]],
    #     1: ["Cue 1", [2, 'Dimmer', 100], [1, 'Dimmer', 50]],
    #     }

    def __init__(self):
        QThread.__init__(self)
        # self.fade_timer=QTimer(self)
        # self.fade_timer.timeout.connect(self.fade_cue)
        # self.fade_timer.start(20)
        #self.global_timer.start(500)

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

    def fade_cue(self):
        if self.fade:
            for lamp in self.lamp_to_fade:
                try:
                    A = [x for x in self.cuelist[self.cur_cue][2:] if lamp[:2] == x[:2]][0][2]
                except IndexError:
                    A = 0
                #B = lamp[2]
                try:
                    B = [x for x in self.cuelist[self.next_cue][2:] if lamp[0] == x[0]][0][2]
                except IndexError:
                    print(self.cuelist[self.next_cue][2:])
                    print(lamp)
                    print([x for x in self.cuelist[self.next_cue][2:] if lamp[0] == x[0]])
                #B = [x[2] for x in self.cuelist[self.next_cue][2:] if lamp == x[:2]][0]
                value=round(A + (time()-self.fade_time_begin)*((B-A)/(self.fade_time_end-self.fade_time_begin)))
                self.lampset.emit(lamp[0], lamp[1], value)
            if time() >= self.fade_time_end:
                for lamp in self.cuelist.get(self.next_cue,self.cuelist[0])[2:]:
                    self.lampset.emit(lamp[0], lamp[1], lamp[2])
                self.fade=False
                self.cur_cue = self.next_cue

    def get_alter_lamps(self, current, _next):
        if _next == current:
            return current
        else:
            return_list = []
            for i in current:
                if not any(i == x for x in _next) or any(i[0] == x[0] and not [i[1],i[2]] == [x[1],x[2]] for x in _next):
                    return_list.append(i)
            return return_list

    def goto(self, cue):
        if cue == -1:
            cue = self.cur_cue + 1
        seq = [x for x in self.cuelist.keys() if not isinstance(x, str)]
        if cue == max(seq)+1 and self.options.get("warp_at_end", False):
            cue = min(seq)
        try:
            self.cuelist[cue]
        except KeyError:
            cue = 0
        try:
            print(self.cuelist.get(cue,self.cuelist[0]))
            if self.cuelist.get(cue,self.cuelist[0])[1] == 0:
                for lamp in self.cuelist.get(cue,self.cuelist[0])[2:]:
                    self.lampset.emit(lamp[0], lamp[1], lamp[2])
                self.cur_cue=cue
            else:
                cur_cue_list = self.cuelist[self.cur_cue][2:]
                next_cue_list = self.cuelist.get(cue,self.cuelist[0])[2:]
                self.lamp_to_fade = self.get_alter_lamps(cur_cue_list,next_cue_list)
                self.next_cue=cue
                self.fade_time_end = time() + self.cuelist.get(cue,self.cuelist[0])[1]
                self.fade_time_begin = time()
                self.fade = True
        except KeyError:
            error_log_global.append("CuelistThread: cue {0:d} not defined".format(cue))

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

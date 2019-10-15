from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from DmxThread import DmxThread
from GlobalVar import typ_to_addr, nr_to_typ, nr_to_addr

class AbstractThread(QThread):
    channelset = pyqtSignal(int, int, int)
    
    def __init__(self):
        QThread.__init__(self)
        
    def run(self):
        dmx_thread = DmxThread()
        self.channelset.connect(dmx_thread.set_channel)
        dmx_thread.start()
        
        loop = QEventLoop()
        loop.exec_()
    
    def get_func_from_type(lamp_type, setting, value):
        return 0, 0
    
    @pyqtSlot(int, str, object)
    def set_lamp(self, lamp, setting, value):
        try:
            lamp_type = nr_to_typ[lamp]
            local_channel, set_value = self.get_func_from_type(lamp_type, setting, value)
            univer, addr = nr_to_addr[lamp]
            self.channelset.emit(univer, addr+local_channel, set_value)
        except NameError:
            print("Something went wrong within the abstraction layer")
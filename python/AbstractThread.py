from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from DmxThread import DmxThread
from GlobalVar import typ_to_addr, nr_to_typ, nr_to_addr

class AbstractThread(QThread):
    channelset = pyqtSignal(int, int, int)
    
    def __init__(self):
        QThread.__init__(self)
        self.dmx_thread = DmxThread()
        
    def run(self):
        self.channelset.connect(self.dmx_thread.set_channel)
        self.dmx_thread.start()
        
        loop = QEventLoop()
        loop.exec_()
    
    def get_func_from_type(self, lamp_type, setting, value):
        channel_plus = typ_to_addr[lamp_type][setting]['Channel']
        if typ_to_addr[lamp_type][setting]['Mode'] == 'normal':
            if any(setting in i for i in ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow']):
                return_value = int(value)
            else:
                return_value = (value / 100) * 255
        return channel_plus, return_value
    
    @pyqtSlot(int, str, object)
    def set_lamp(self, lamp, setting, value):
        try:
            lamp_type = nr_to_typ[lamp]
            local_channel, set_value = self.get_func_from_type(lamp_type, setting, value)
            #if setting == 'Intensity' or setting == 'Dimmer':
                #set_value = set_value
            univer, addr = nr_to_addr[lamp]
            self.channelset.emit(univer, addr+local_channel, set_value)
        except NameError:
            print("Something went wrong within the abstraction layer")

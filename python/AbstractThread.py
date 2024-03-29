from PyQt5.QtCore import QThread, QEventLoop, pyqtSignal, pyqtSlot

from DmxThread import DmxThread
from GlobalVar import typ_to_addr, nr_to_typ, nr_to_addr, error_log_global

class AbstractThread(QThread):
    channelset = pyqtSignal(int, int, int)
    send_artnet_all = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.dmx_thread = DmxThread()

    def run(self):
        self.channelset.connect(self.dmx_thread.set_channel)
        self.dmx_thread.start()
        self.send_artnet_all.connect(self.dmx_thread.send_artnet_all_sock)

        loop = QEventLoop()
        loop.exec_()

    def get_func_from_type(self, lamp_type, setting, value):
        channel_plus = typ_to_addr[lamp_type][setting]['Channel']
        if typ_to_addr[lamp_type][setting]['Mode'] == 'normal':
            if any(setting in i for i in ['Red', 'Green', 'Blue', 'Cyan', 'Magenta', 'Yellow']):
                return_value = int(value)
            else:
                return_value = (value / 100) * 255
        else:
            return_value = 0
        return channel_plus, return_value

    @pyqtSlot(int, str, object)
    def set_lamp(self, lamp, setting, value):
        try:
            lamp_type = nr_to_typ[lamp]
            try:
                local_channel, set_value = self.get_func_from_type(lamp_type, setting, value)
            except KeyError:
                error_log_global.append("AbstractThread: Fixturetype {0:s} not found".format(lamp_type))
                return
            #if setting == 'Intensity' or setting == 'Dimmer':
                #set_value = set_value
            univer, addr = nr_to_addr[lamp]
            self.channelset.emit(univer, addr+local_channel, set_value)
        except NameError:
            error_log_global.append("AbstractThread: Name not found!")
        except KeyError:
            error_log_global.append("AbstractThread: Fixture {0:d} not found!".format(lamp))

    def send_artnet_all_sock_relay(self):
        self.send_artnet_all.emit()

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import serial

class SerialThread(QThread):
    keystroke = pyqtSignal(str, bool)
    fadermove = pyqtSignal(str, int)
    encodermove = pyqtSignal(str, int)
    send_error = pyqtSignal(str)
    
    serial_send_buffer = ''
    
    def __init__(self):
        QThread.__init__(self)
        while 1:
            try:
                self.ser = serial.Serial("/dev/faderkeys", 115200)
                break
            except serial.serialutil.SerialException:
                self.send_error("SerialThread: Serial exception")
        self.ser.reset_input_buffer()
        self.serial_send_timer = QTimer(self)
    
    def run(self):
        self.serial_send_timer.start(300)
        while 1:
            try:
                serial_get = str(self.ser.readline())
                if "A" in serial_get:
                    spacer = serial_get.index(":")
                    self.fadermove.emit(serial_get[3:spacer], int(serial_get[spacer+1:-5]))
                elif "E" in serial_get:
                    spacer = serial_get.index(":")
                    self.encodermove.emit(serial_get[3:spacer], int(serial_get[spacer+1:-5]))
                else:
                    self.keystroke.emit(serial_get[2:-6], bool(int(serial_get[-6])))
            except:
                self.send_error.emit("SerialThread: {0:s} failed".format(serial_get))
    
    @pyqtSlot(int, int)
    def set_fader(self, fader, value):
        serial_send_buffer += "A{0:d}:{1:d}\n".format(fader,value)
    
    def send_serial(self):
        if self.serial_send_buffer != '':
            self.ser.write(bytearray((serial_send_buffer+";").encode()))
            self.serial_send_buffer = ''

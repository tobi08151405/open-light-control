from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import serial

class SerialThread(QThread):
    keystroke = pyqtSignal(str, bool)
    fadermove = pyqtSignal(str, int)
    encodermove = pyqtSignal(str, int)
    send_error = pyqtSignal(str)
    
    def __init__(self):
        QThread.__init__(self)
        while 1:
            try:
                self.ser = serial.Serial("/dev/faderkeys", 115200)
                break
            except serial.serialutil.SerialException:
                self.send_error("SerialThread: Serial exception")
        self.ser.reset_input_buffer()
    
    def run(self):
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
                self.send_error("SerialThread: parsing failed")

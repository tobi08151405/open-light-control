from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QThread

from GlobalVar import error_log_global

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
                error_log_global.append("SerialThread: Serial exception")
        self.ser.reset_input_buffer()
        self.serial_send_timer = QTimer(self)
        self.serial_send_timer.timeout.connect(self.send_serial)
        self.serial_send_timer.start(500)

    def run(self):
        while 1:
            serial_get = ""
            try:
                serial_get = str(self.ser.readline())
                if "A" in serial_get:
                    spacer = serial_get.index(":")
                    self.fadermove.emit(
                        serial_get[3:spacer], int(serial_get[spacer+1:-5]))
                elif "E" in serial_get:
                    spacer = serial_get.index(":")
                    self.encodermove.emit(
                        serial_get[3:spacer], int(serial_get[spacer+1:-5]))
                else:
                    self.keystroke.emit(
                        serial_get[2:-6], bool(int(serial_get[-6])))
            except:
                error_log_global.append(
                    "SerialThread: {0:s} failed".format(serial_get))

    @pyqtSlot(int, int)
    def set_fader(self, fader, value):
        self.serial_send_buffer += "A{0:d}:{1:d},".format(fader, value)

    def send_serial(self):
        if self.serial_send_buffer != '':
            self.serial_send_buffer += ";"
            self.ser.write(bytearray(self.serial_send_buffer.encode()))
            self.serial_send_buffer = ''

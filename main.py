from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import struct
import sys
import serial
import socket
import os
from time import time

serial_enable = False

rows = 2
cols = 2
faders = 2
universe_num = 4
uni_map = dict(zip(range(universe_num), range(universe_num)))
uni_map_ = {v: k for k, v in uni_map.items()}

def change_uni(from_, to_):
    uni_map[uni_map_[int(from_)]] = int(to_)
    uni_map_ = {v: k for k, v in uni_map.items()}

class ArtnetThread(QThread):    
    uni_list = []
    for i in range(universe_num):
        uni_list.append([])
    
    for uni in uni_list:
        for i in range(512):
            uni.append(0)
    
    artnet_prefix = bytearray([0x41, 0x72, 0x74, 0x2d, 0x4e, 0x65, 0x74, 0x00, 0x00, 0x50, 0x00, 0x0e, 0x00, 0x00])
    
    def __init__(self):
        QThread.__init__(self)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        self.sock.settimeout(5)
        self.artnet_timer = QTimer(self)
        self.artnet_timer.timeout.connect(self.send_artnet_all)
        self.artnet_timer.start(4000)
    
    def run(self):
        input("")
    
    def send_artnet_all(self):
        for uni in range(universe_num):
            self.send_artnet(uni)
    
    def send_artnet(self, uni):
        packet = self.artnet_prefix.copy()
        packet+=struct.pack(">h", uni_map[uni])+struct.pack(">h", 512)
        for chan in self.uni_list[uni]:
            packet+=struct.pack("B", chan)
        self.sock.sendto(packet, ('255.255.255.255', 6454))
        
    @pyqtSlot(int, int, int)
    def set_channel(universe, channel, value):
        self.uni_list[universe][channel] = int(value)
        self.send_artnet(uni)

class SerialThread(QThread):
    keystroke = pyqtSignal(str, bool)
    fadermove = pyqtSignal(str, int)
    
    def __init__(self):
        QThread.__init__(self)
        while 1:
            try:
                self.ser = serial.Serial("/dev/faderkeys", 115200)
                break
            except serial.serialutil.SerialException:
                pass
        self.ser.reset_input_buffer()
    
    def __del__(self):
        self.wait()
    
    def run(self):
        while 1:
            try:
                serial_get = str(self.ser.readline())
                if "A" in serial_get:
                    spacer = serial_get.index(":")
                    self.fadermove.emit(serial_get[3:spacer], int(serial_get[spacer+1:-5]))
                else:
                    self.keystroke.emit(serial_get[2:-6], bool(int(serial_get[-6])))
            except:
                pass

class MainWindow(QMainWindow):
    channelset = pyqtSignal(int, int, int)
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Serial Test")
        
        if serial_enable:
            serial_thread = SerialThread()
            serial_thread.keystroke.connect(self.map_keys)
            serial_thread.fadermove.connect(self.map_faders)
            serial_thread.start()
        
        artnet_thread = ArtnetThread()
        self.channelset.connect(artnet_thread.set_channel)
        artnet_thread.start()
        
        self.layout = QGridLayout()
        
        for row in range(rows):
            for col in range(cols):
                num = (row * cols) + col
                exec("self.key"+str(num)+"=QPushButton()")
                exec("self.key"+str(num)+".setCheckable(True)")
                exec("self.layout.addWidget(self.key"+str(num)+","+str(row)+","+str(col)+")")
        
        for fader in range(faders):
            exec("self.fader"+str(fader)+"=QLabel()")
            exec("self.fader"+str(fader)+".setAlignment(Qt.AlignCenter)")
            exec("self.layout.addWidget(self.fader"+str(fader)+","+str(rows+1)+","+str(fader)+")")
        
        sortact = QAction('Sort', self)
        sortact.triggered.connect(self.sort)
        
        quitact = QAction('Quit', self)
        quitact.triggered.connect(self.close)
        
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(sortact)
        self.fileMenu.addAction(quitact)
        
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        
        self.mdi = QMdiArea()
        
        self.sub = QMdiSubWindow()
        self.sub.setWidget(self.widget)
        self.mdi.addSubWindow(self.sub)
        self.sub.show()
        
        self.setCentralWidget(self.mdi)
    
    def sort(self):
        self.mdi.tileSubWindows()
    
    @pyqtSlot(str, bool)
    def map_keys(self, key, pressed):
        if pressed:
            exec("self.key"+key+".setChecked(True)")
            exec("self.key"+key+".setText('pressed')")
        else:
            exec("self.key"+key+".setChecked(False)")
            exec("self.key"+key+".setText('')")
            
    @pyqtSlot(str, int)
    def map_faders(self, fader, value):
        exec("self.fader"+fader+".setText('"+str(value)+"')")

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import struct
import sys
import serial
import socket

serial_enable = False

rows = 4
cols = 3
faders = 3
encoders = 1
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
    encodermove = pyqtSignal(str, int)
    
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
                elif "E" in serial_get:
                    spacer = serial_get.index(":")
                    self.encodermove.emit(serial_get[3:spacer], int(serial_get[spacer+1:-5]))
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
            serial_thread.encodermove.connect(self.map_encoders)
            serial_thread.start()
        
        artnet_thread = ArtnetThread()
        self.channelset.connect(artnet_thread.set_channel)
        artnet_thread.start()
        
        sortact = QAction('Sort', self)
        sortact.triggered.connect(self.sort)
        
        quitact = QAction('Quit', self)
        quitact.triggered.connect(self.close)
        
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(sortact)
        self.fileMenu.addAction(quitact)
        
        self.mdi = QMdiArea()
        
        self.create_encoders()
        self.create_faders()
        self.create_keys()
        
        self.setCentralWidget(self.mdi)
    
    def create_keys(self):
        self.keys_layout = QGridLayout()
        for row in range(rows):
            for col in range(cols):
                num = (row * cols) + col
                exec("self.key{0:d}=QPushButton()".format(num))
                exec("self.key{0:d}.setCheckable(True)".format(num))
                exec("self.keys_layout.addWidget(self.key{0:d},{1:d},{2:d})".format(num,row,col))
        self.keys_widget = QWidget()
        self.keys_widget.setLayout(self.keys_layout)
        self.keys_sub = QMdiSubWindow()
        self.keys_sub.setWidget(self.keys_widget)
        self.mdi.addSubWindow(self.keys_sub)
        self.keys_sub.show()
    
    def create_faders(self):
        self.faders_layout = QGridLayout()
        for fader in range(faders):
            exec("self.fader{0:d}=QLabel()".format(fader))
            exec("self.fader{0:d}.setAlignment(Qt.AlignCenter)".format(fader))
            exec("self.fader{0:d}.setText('0')".format(fader))
            exec("self.faders_layout.addWidget(self.fader{0:d},0,{0:d})".format(fader))
        self.faders_widget = QWidget()
        self.faders_widget.setLayout(self.faders_layout)
        self.faders_sub = QMdiSubWindow()
        self.faders_sub.setWidget(self.faders_widget)
        self.mdi.addSubWindow(self.faders_sub)
        self.faders_sub.show()
        
    def create_encoders(self):
        self.encoders_layout = QGridLayout()
        for encoder in range(encoders):
            exec("self.encoder{0:d}=QLabel()".format(encoder))
            exec("self.encoder{0:d}.setAlignment(Qt.AlignCenter)".format(encoder))
            exec("self.encoder{0:d}.setText('0')".format(encoder))
            exec("self.encoders_layout.addWidget(self.encoder{0:d},0,{0:d})".format(encoder))
        self.encoders_widget = QWidget()
        self.encoders_widget.setLayout(self.encoders_layout)
        self.encoders_sub = QMdiSubWindow()
        self.encoders_sub.setWidget(self.encoders_widget)
        self.mdi.addSubWindow(self.encoders_sub)
        self.encoders_sub.show()
    
    def sort(self):
        self.mdi.tileSubWindows()
    
    @pyqtSlot(str, bool)
    def map_keys(self, key, pressed):
        try:
            if pressed:
                exec("self.key{0:s}.setChecked(True)".format(key))
                exec("self.key{0:s}.setText('pressed')".format(key))
            else:
                exec("self.key{0:s}.setChecked(False)".format(key))
                exec("self.key{0:s}.setText('')".format(key))
        except NameError:
            print("button {0:s} not found!".format(key))
            
    @pyqtSlot(str, int)
    def map_faders(self, fader, value):
        try:
            exec("self.fader{0:s}.setText('{1:d}')".format(fader,value))
        except NameError:
            print("fader {0:s} not found!".format(fader))
    
    @pyqtSlot(str, int)
    def map_encoders(self, encoder, value):
        try:
            exec("cur = int(self.encoder{0:s}.text())".format(encoder))
            exec("self.encoder{0:s}.setText('{1:d}')".format(encoder, cur-value))
        except NameError:
            print("encoder {0:s} not found!".format(encoder))

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec_())

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import json
import time

from GlobalVar import *
from SerialThread import SerialThread
from AbstractThread import AbstractThread
import Create_lamps

Create_lamps.create()

def change_uni(from_, to_):
    global uni_map
    global uni_map_
    uni_map[uni_map_[int(from_)]] = int(to_)
    uni_map_ = {v: k for k, v in uni_map.items()}

class MainWindow(QMainWindow):
    lampset = pyqtSignal(int, str, object)
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Serial Test")
        
        if serial_enable:
            serial_thread = SerialThread()
            serial_thread.keystroke.connect(self.map_keys)
            serial_thread.fadermove.connect(self.map_faders)
            serial_thread.encodermove.connect(self.map_encoders)
            serial_thread.start()
        
        abstract_thread = AbstractThread()
        self.lampset.connect(abstract_thread.set_lamp)
        abstract_thread.start()
        
        sortact = QAction('Sort', self)
        sortact.triggered.connect(self.sort)
        
        quitact = QAction('Quit', self)
        quitact.triggered.connect(self.close)
        
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(sortact)
        self.fileMenu.addAction(quitact)
        
        self.mdi = QMdiArea()
        
        #self.create_encoders()
        #self.create_faders()
        #self.create_keys()
        self.create_test()
        
        self.setCentralWidget(self.mdi)
    
    def create_test(self):
        self.test_layout = QGridLayout()
        self.test0=QPushButton()
        self.test0.clicked.connect(self.test_artnet2)
        self.test1=QPushButton()
        self.test1.clicked.connect(self.test_artnet1)
        self.test_layout.addWidget(self.test0,0,0)
        self.test_layout.addWidget(self.test1,0,1)
        self.test_widget = QWidget()
        self.test_widget.setLayout(self.test_layout)
        self.test_sub = QMdiSubWindow()
        self.test_sub.setWidget(self.test_widget)
        self.mdi.addSubWindow(self.test_sub)
        self.test_sub.show()
    
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
    
    def test_artnet(self):
        self.lampset.emit(110, "Dimmer", 100)
        self.lampset.emit(110, "Red", 255)
    
    def test_artnet1(self):
        self.lampset.emit(7, "Intensity", 100)
    
    def test_artnet2(self):
        self.lampset.emit(100, "Dimmer", 100)
        self.lampset.emit(100, "CTB", 100)
    
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
#print(typ_to_func,typ_to_addr)
sys.exit(app.exec_())

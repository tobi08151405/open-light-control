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
import Reverser

Create_lamps.create()
Reverser.create_typ_to_func(["../dev/ofl-json/tao-led.json","../dev/ofl-json/generic/desk-channel.json","../dev/ofl-json/michi.json"])
Reverser.create_typ_to_addr(["../dev/ofl-json/tao-led.json","../dev/ofl-json/generic/desk-channel.json","../dev/ofl-json/michi.json"])

def change_uni(from_, to_):
    global uni_map
    global uni_map_
    uni_map[uni_map_[int(from_)]] = int(to_)
    uni_map_ = {v: k for k, v in uni_map.items()}

class MainWindow(QMainWindow):
    lampset = pyqtSignal(int, str, object)
    master_change = pyqtSignal(int)
    
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
        self.master_change.connect(abstract_thread.dmx_thread.set_master)
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
        self.create_gezeit()
        self.create_master_fader()
        #self.create_color()
        #self.create_test()
        
        self.setCentralWidget(self.mdi)
        
    def create_gezeit(self):
        self.gez_layout = QGridLayout()
        
        self.pub_slid = QSlider()
        self.pub_slid.setMinimum(0)
        self.pub_slid.setMaximum(100)
        self.pub_slid.valueChanged.connect(self.pub_slid_fader)
        self.gez_layout.addWidget(QLabel("Pub"),0,0)
        self.gez_layout.addWidget(self.pub_slid,1,0)
        
        self.schlaf_slid = QSlider()
        self.schlaf_slid.setMinimum(0)
        self.schlaf_slid.setMaximum(100)
        self.schlaf_slid.valueChanged.connect(self.schlaf_slid_fader)
        self.gez_layout.addWidget(QLabel("Schlafz"),0,1)
        self.gez_layout.addWidget(self.schlaf_slid,1,1)
        
        self.berg1 = QSlider()
        self.berg1.setMinimum(0)
        self.berg1.setMaximum(100)
        self.berg1.valueChanged.connect(self.berg1_fader)
        self.gez_layout.addWidget(QLabel("Berg 1"),0,2)
        self.gez_layout.addWidget(self.berg1,1,2)
        
        self.bergg = QSlider()
        self.bergg.setMinimum(0)
        self.bergg.setMaximum(100)
        self.bergg.valueChanged.connect(self.bergg_fader)
        self.gez_layout.addWidget(QLabel("Berg G"),0,3)
        self.gez_layout.addWidget(self.bergg,1,3)
        
        self.gez_widget = QWidget()
        self.gez_widget.setLayout(self.gez_layout)
        self.gez_sub = QMdiSubWindow()
        self.gez_sub.setWidget(self.gez_widget)
        self.mdi.addSubWindow(self.gez_sub)
        self.gez_sub.show()
    
    def create_master_fader(self):
        self.master_sli_layout = QGridLayout()
        self.mslider=QSlider()
        self.mslider.setMinimum(0)
        self.mslider.setMaximum(100)
        self.mslider.valueChanged.connect(self.master_sli_fader)
        self.master_sli_layout.addWidget(QLabel("Master"))
        self.master_sli_layout.addWidget(self.mslider)
        self.master_sli_widget = QWidget()
        self.master_sli_widget.setLayout(self.master_sli_layout)
        self.master_sli_sub = QMdiSubWindow()
        self.master_sli_sub.setWidget(self.master_sli_widget)
        self.mdi.addSubWindow(self.master_sli_sub)
        self.master_sli_sub.show()
    
    def create_color(self):
        self.color_layout = QGridLayout()
        self.color_dia0 = QColorDialog()
        self.color_dia0.setOption(2)
        self.color_dia0.currentColorChanged.connect(self.test_colors)
        self.color_layout.addWidget(self.color_dia0)
        self.color_widget = QWidget()
        self.color_widget.setLayout(self.color_layout)
        self.color_sub = QMdiSubWindow()
        self.color_sub.setWidget(self.color_widget)
        self.mdi.addSubWindow(self.color_sub)
        self.color_sub.show()
    
    def create_test(self):
        self.test_layout = QGridLayout()
        self.test0=QPushButton()
        self.test0.clicked.connect(self.test_artnet2)
        self.test1=QPushButton()
        self.test1.clicked.connect(self.test_artnet1)
        self.test2=QSlider()
        self.test2.setMinimum(0)
        self.test2.setMaximum(100)
        self.test2.valueChanged.connect(self.test_slider)
        self.test_layout.addWidget(self.test0,0,0)
        self.test_layout.addWidget(self.test1,0,1)
        self.test_layout.addWidget(self.test2,0,2)
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
        self.lampset.emit(100, 'White', 100)
        
    def test_artnet3(self):
        self.lampset.emit(100, 'Dimmer', 0)
    
    @pyqtSlot(int)
    def master_sli_fader(self, i):
        self.master_change.emit(i)
        
    @pyqtSlot(int)
    def schlaf_slid_fader(self, i):
        self.lampset.emit(35, 'Intensity', i)
        self.lampset.emit(40, 'Intensity', i)
    
    @pyqtSlot(int)
    def berg1_fader(self, i):
        self.lampset.emit(32, 'Intensity', i)
        
    @pyqtSlot(int)
    def bergg_fader(self, i):
        self.lampset.emit(14, 'Intensity', i)
        self.lampset.emit(19, 'Intensity', i)
        self.lampset.emit(36, 'Intensity', i)
        
    @pyqtSlot(int)
    def pub_slid_fader(self, i):
        self.lampset.emit(7, 'Intensity', i)
        self.lampset.emit(17, 'Intensity', i)
        self.lampset.emit(21, 'Intensity', i)
        self.lampset.emit(26, 'Intensity', i)
        
    
    @pyqtSlot(int)
    def test_slider(self, sli):
        for i in range(111,117):
            self.lampset.emit(i, 'Dimmer', sli)
            
    @pyqtSlot(QColor)
    def test_colors(self, col):
        for i in range(111,117):
            self.lampset.emit(i, 'Red', col.red())
            self.lampset.emit(i, 'Green', col.green())
            self.lampset.emit(i, 'Blue', col.blue())
    
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
#print(nr_to_addr,nr_to_typ,typ_to_func,typ_to_addr)
sys.exit(app.exec_())

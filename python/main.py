from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import json
import time
import math
import colorsys

import pdb

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
    
    freq=1
    add_fac=0.01
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Serial Test")
        
        if serial_enable:
            serial_thread = SerialThread()
            serial_thread.keystroke.connect(self.map_keys)
            serial_thread.fadermove.connect(self.map_faders)
            serial_thread.encodermove.connect(self.map_encoders)
            serial_thread.send_error.connect(self.update_error_log)
            serial_thread.start()
        
        abstract_thread = AbstractThread()
        self.lampset.connect(abstract_thread.set_lamp)
        self.master_change.connect(abstract_thread.dmx_thread.set_master)
        abstract_thread.send_error.connect(self.update_error_log)
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
        self.mdi.setFont(QFont('Sans Serif', 12))
        
        #self.create_encoders()
        #self.create_faders()
        #self.create_keys()
        #self.create_gezeit()
        self.create_best()
        self.create_master_fader()
        self.create_error_log()
        #self.create_color()
        #self.create_test()
        self.create_chase_test()
        
        self.chase_timer=QTimer(self)
        self.chase_timer.timeout.connect(self.chase_send)
        
        self.setCentralWidget(self.mdi)
        #pdb.set_trace()
    
    def create_sub_area(self, name, title, wid_list, width=None):
        exec("self.{0:s}_layout = QGridLayout()".format(name))
        for wid in wid_list:
            exec("self.{0:s}_layout.addWidget(wid[0],wid[1],wid[2])".format(name))
        if width:
            exec("self.col_count=self.{0:s}_layout.columnCount()".format(name))
            for col in range(self.col_count):
                exec("self.{0:s}_layout.setColumnMinimumWidth(col,{1:d})".format(name,width))
        exec("self.{0:s}_widget = QWidget()\nself.{0:s}_widget.setLayout(self.{0:s}_layout)\nself.{0:s}_scroll=QScrollArea()\nself.{0:s}_scroll.setWidget(self.{0:s}_widget)\nself.{0:s}_sub = QMdiSubWindow()\nself.{0:s}_sub.setWidget(self.{0:s}_scroll)\nself.{0:s}_sub.setWindowTitle('{1:s}')\nself.mdi.addSubWindow(self.{0:s}_sub)\nself.{0:s}_sub.show()".format(name, title))
    
    def create_fader(self, name, label, liste, start, start1):
        exec("self.{0:s}_slid = QSlider()\nself.{0:s}_slid.setMinimum(0)\nself.{0:s}_slid.setMaximum(100)\nself.{0:s}_slid.valueChanged.connect(self.{0:s}_slid_fader)\nliste.append([QLabel('{1:s}'),start,start1])\nliste.append([self.{0:s}_slid,start+1,start1])".format(name, label))
    
    def create_chase_test(self):
        chase_list=[]
        
        self.chase_edit=QLineEdit()
        self.chase_edit.returnPressed.connect(self.chase_update)
        chase_list.append([self.chase_edit,0,0])
        self.chase_abs_edit=QLineEdit()
        self.chase_abs_edit.returnPressed.connect(self.chase_abs_update)
        chase_list.append([self.chase_abs_edit,1,0])
        
        self.chase_start=QPushButton("Start")
        self.chase_start.clicked.connect(lambda: self.chase_timer.start(10))
        chase_list.append([self.chase_start, 0, 1])
        self.chase_stop=QPushButton("Stop")
        self.chase_stop.clicked.connect(lambda: self.chase_timer.stop())
        chase_list.append([self.chase_stop, 1, 1])
        
        self.create_sub_area("chase_test", "LED Chase", chase_list, width=70)
    
    def create_gezeit(self):
        gez_list = []
        
        self.pub_slid = QSlider()
        self.pub_slid.setMinimum(0)
        self.pub_slid.setMaximum(100)
        self.pub_slid.valueChanged.connect(self.pub_slid_fader)
        gez_list.append([QLabel("Pub"),0,0])
        gez_list.append([self.pub_slid,1,0])
        
        self.schlaf_slid = QSlider()
        self.schlaf_slid.setMinimum(0)
        self.schlaf_slid.setMaximum(100)
        self.schlaf_slid.valueChanged.connect(self.schlaf_slid_fader)
        gez_list.append([QLabel("Schlafz"),0,1])
        gez_list.append([self.schlaf_slid,1,1])
        
        self.berg1 = QSlider()
        self.berg1.setMinimum(0)
        self.berg1.setMaximum(100)
        self.berg1.valueChanged.connect(self.berg1_fader)
        gez_list.append([QLabel("Berg 1"),0,2])
        gez_list.append([self.berg1,1,2])
        
        self.bergg = QSlider()
        self.bergg.setMinimum(0)
        self.bergg.setMaximum(100)
        self.bergg.valueChanged.connect(self.bergg_fader)
        gez_list.append([QLabel("Berg G"),0,3])
        gez_list.append([self.bergg,1,3])
        
        self.create_sub_area("gez", "GeHzeiten", gez_list, width=70)
    
    def create_error_log(self):
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(1)
        self.create_sub_area("error", "Error Log", [[self.error_text, 0, 0]])
    
    def create_master_fader(self):
        master_list = []
        
        self.mslider=QSlider()
        self.mslider.setMinimum(0)
        self.mslider.setMaximum(100)
        self.mslider_max_button=QPushButton("Max")
        self.mslider_min_button=QPushButton("Min")
        self.mslider.valueChanged.connect(self.master_sli_fader)
        self.mslider_max_button.clicked.connect(self.set_master_max)
        self.mslider_min_button.clicked.connect(self.set_master_min)
        width_edit=QLineEdit()
        width_edit.setPlaceholderText(str(self.mslider.size().width()))
        height_edit=QLineEdit()
        height_edit.setPlaceholderText(str(self.mslider.size().height()))
        width_edit.returnPressed.connect(lambda: self.mslider.resize(QSize(int(width_edit.text()),self.mslider.size().height())))
        height_edit.returnPressed.connect(lambda: self.mslider.resize(QSize(self.mslider.size().width(),int(height_edit.text()))))
        master_list.append([self.mslider, 0, 0])
        master_list.append([self.mslider_max_button, 0, 1])
        master_list.append([self.mslider_min_button, 1, 1])
        master_list.append([width_edit, 0, 2])
        master_list.append([height_edit, 1, 2])
        
        self.create_sub_area("mslider", "Master", master_list)
    
    def create_color(self):
        self.color_dia0 = QColorDialog()
        self.color_dia0.setOption(2)
        self.color_dia0.currentColorChanged.connect(self.test_colors)
        
        self.create_sub_area("color", "Color Changer", [[self.color_dia0, 0, 0]])
    
    def create_test(self):
        test_list = []
        
        self.test0=QPushButton()
        self.test0.clicked.connect(self.test_artnet2)
        self.test1=QPushButton()
        self.test1.clicked.connect(self.test_artnet1)
        self.test2=QSlider()
        self.test2.setMinimum(0)
        self.test2.setMaximum(100)
        self.test2.valueChanged.connect(self.test_slider)
        test_list.append([self.test0,0,0])
        test_list.append([self.test1,0,1])
        test_list.append([self.test2,0,2])
        
        self.create_sub_area("test", "Test Area", test_list)
    
    def create_keys(self):
        keys_list=[]
        for row in range(rows):
            for col in range(cols):
                num = (row * cols) + col
                exec("self.key{0:d}=QPushButton()".format(num))
                exec("self.key{0:d}.setCheckable(True)".format(num))
                exec("keys_list.append([self.key{0:d},{1:d},{2:d}])".format(num,row,col))
        self.create_sub_area("keys", "Buttons", keys_list)
    
    def create_faders(self):
        faders_list=[]
        for fader in range(faders):
            exec("self.fader{0:d}=QLabel()".format(fader))
            exec("self.fader{0:d}.setAlignment(Qt.AlignCenter)".format(fader))
            exec("self.fader{0:d}.setText('0')".format(fader))
            exec("faders_list.append([self.fader{0:d},0,{0:d}])".format(fader))
        self.create_sub_area("faders", "Faders", faders_list, width=30)
        
    def create_encoders(self):
        encoder_list=[]
        for encoder in range(encoders):
            exec("self.encoder{0:d}=QLabel()".format(encoder))
            exec("self.encoder{0:d}.setAlignment(Qt.AlignCenter)".format(encoder))
            exec("self.encoder{0:d}.setText('0')".format(encoder))
            exec("encoder_list.append([self.encoder{0:d},0,{0:d}])".format(encoder))
        self.create_sub_area("encoders", "Encoders", encoder_list, width=30)
    
    def create_best(self):
        best_list = []
        
        self.create_fader("christ", "Christine", best_list, 0, 0)
        self.create_fader("lied", "Lied", best_list, 0, 1)
        self.create_fader("tanz", "Tanz", best_list, 0, 2)
        self.create_fader("andi", "Andi", best_list, 0, 3)
        self.create_fader("rap", "Rap", best_list, 0, 4)
        self.create_fader("elli", "Elli", best_list, 0, 5)
        self.create_fader("mod", "Moderation", best_list, 0, 6)
        self.create_fader("pub", "Pub", best_list, 0, 7)
        
        self.create_sub_area("best", "Best of", best_list, width=80)
    
    def christ_slid_fader(self, i):
        self.lampset(30, "Intensity", i)
        self.lampset(45, "Intensity", i*0.5)
        self.lampset(46, "Intensity", i*0.5)
        
    def lied_slid_fader(self, i):
        self.lampset(25, "Intensity", i)
        self.lampset(30, "Intensity", i)
        for led in range(110,116):
            self.lampset(led, "Dimmer", i*0.3)
            self.lampset(led, "Red", 255)
            self.lampset(led, "Green", 255)
            self.lampset(led, "Blue", 0)
    
    def tanz_slid_fader(self, i):
        self.lampset(20, "Intensity", i)
        self.lampset(17, "Intensity", i)
        self.lampset(26, "Intensity", i)
        self.lampset(29, "Intensity", i)
        for led in range(110,116):
            self.lampset(led, "Dimmer", i*0.6)
            self.lampset(led, "Red", 255)
            self.lampset(led, "Green", 0)
            self.lampset(led, "Blue", 255)
    
    def andi_slid_fader(self, i):
        self.lampset(20, "Intensity", i*0.45)
        self.lampset(17, "Intensity", i*0.45)
        
    def rap_slid_fader(self, i):
        for led in range(110,116):
            self.lampset(led, "Dimmer", i)
            self.lampset(led, "Red", 255)
            self.lampset(led, "Green", 255)
            self.lampset(led, "Blue", 255)
    
    def elli_slid_fader(self, i):
        self.lampset(17, "Intensity", i*0.8)
        self.lampset(30, "Intensity", i*0.6)
        for led in range(110,116):
            self.lampset(led, "Dimmer", i*0.25)
            self.lampset(led, "Red", 255)
            self.lampset(led, "Green", 0)
            self.lampset(led, "Blue", 0)
            
    def mod_slid_fader(self, i):
        self.lampset(21, "Intensity", i)
        self.lampset(17, "Intensity", i)
        self.lampset(26, "Intensity", i*0.6)
        self.lampset(29, "Intensity", i*0.6)
        for led in range(110,116):
            self.lampset(led, "Dimmer", i*0.3)
            self.lampset(led, "Red", 255)
            self.lampset(led, "Green", 255)
            self.lampset(led, "Blue", 0)
            
    def pub_slid_fader(self, i):
        self.lampset(10, "Intensity", i)
        self.lampset(19, "Intensity", i)
        self.lampset(7, "Intensity", i)
    
    def sort(self):
        self.mdi.tileSubWindows()
    
    def chase_update(self):
        temp_freq = float(self.chase_edit.text())
        self.freq = temp_freq
    
    def chase_abs_update(self):
        self.add_fac = float(self.chase_abs_edit.text())
        
    def chase_send(self):
        for i in range(110,116):
            color_tup = colorsys.hsv_to_rgb(abs(math.sin(self.freq*time.time()+(self.add_fac*(i-110)))),1,1)
            self.lampset.emit(i,"Red",color_tup[0]*255)
            self.lampset.emit(i,"Blue",color_tup[1]*255)
            self.lampset.emit(i,"Green",color_tup[2]*255)
    
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
    
    def set_master_max(self):
        self.mslider.setValue(self.mslider.maximum())
    
    def set_master_min(self):
        self.mslider.setValue(self.mslider.minimum())
    
    @pyqtSlot(str)
    def update_error_log(self, er):
        self.error_text.append(er)# + "\n")
    
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
        for i in range(110,116):
            self.lampset.emit(i, 'Dimmer', sli)
            
    @pyqtSlot(QColor)
    def test_colors(self, col):
        for i in range(110,116):
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

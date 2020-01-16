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
import GlobalVar
from SerialThread import SerialThread
from AbstractThread import AbstractThread
from CuelistThread import CuelistThread
from XY_Pad import XY_Pad
import Create_lamps
import Reverser

Create_lamps.create()
#Reverser.create_typ_to_func(["../dev/ofl-json/tao-led.json","../dev/ofl-json/generic/desk-channel.json","../dev/ofl-json/michi.json"])
#Reverser.create_typ_to_addr(["../dev/ofl-json/tao-led.json","../dev/ofl-json/generic/desk-channel.json","../dev/ofl-json/michi.json"])
Reverser.create_typ_to_func(["../dev/ofl-json/generic/rgb-fader.json","../dev/ofl-json/sola-wash.json"])
Reverser.create_typ_to_addr(["../dev/ofl-json/generic/rgb-fader.json","../dev/ofl-json/sola-wash.json"])

def change_uni(from_, to_):
    global uni_map
    global uni_map_
    uni_map[uni_map_[int(from_)]] = int(to_)
    uni_map_ = {v: k for k, v in uni_map.items()}

class MainWindow(QMainWindow):
    lampset = pyqtSignal(int, str, object)
    master_change = pyqtSignal(int)
    faderset = pyqtSignal(int, int)
    
    freq=1
    add_fac=0.01
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setFont(QFont('Sans Serif', 12))
        self.setWindowTitle("Open-light-control")
        
        self.global_timer=QTimer(self)
        self.global_timer.timeout.connect(self.update_error_log)
        self.global_timer.start(500)
        
        if serial_enable:
            self.serial_thread = SerialThread()
            self.serial_thread.keystroke.connect(self.map_keys)
            self.serial_thread.fadermove.connect(self.map_faders)
            self.serial_thread.encodermove.connect(self.map_encoders)
            self.faderset.connect(self.serial_thread.set_fader)
            self.serial_thread.start()
        
        self.abstract_thread = AbstractThread()
        self.lampset.connect(self.abstract_thread.set_lamp)
        self.master_change.connect(self.abstract_thread.dmx_thread.set_master)
        self.abstract_thread.start()
        
        sortact = QAction('Sort', self)
        sortact.triggered.connect(self.sort)
        
        quitact = QAction('Quit', self)
        quitact.triggered.connect(self.close)
        
        mainfadact = QAction('Main Fader', self)
        mainfadact.triggered.connect(self.create_master_fader)
        
        errorlogact = QAction('Error Log', self)
        errorlogact.triggered.connect(self.create_error_log)
        
        self.freezelabel = QAction("Output freezed", self)
        self.freezelabel.setDisabled(True)
        
        self.freezeact = QAction('Freeze Output', self)
        self.freezeact.setCheckable(True)
        self.freezeact.toggled.connect(self.toggle_freeze)
        self.freezeact.toggle()
        
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(mainfadact)
        self.fileMenu.addAction(errorlogact)
        self.fileMenu.addAction(quitact)
        self.toolsMenu = self.menubar.addMenu('Tools')
        self.toolsMenu.addAction(sortact)
        self.toolsMenu.addAction(self.freezeact)
        
        self.status_menubar = QMenuBar(self)
        self.status_menubar.addAction(self.freezelabel)
        
        self.menubar.setCornerWidget(self.status_menubar)
        
        
        self.cuelist_thread = CuelistThread()
        self.cuelist_thread.lampset.connect(self.forward_cuelist_lampset)
        #self.cuelist_thread._go()
        #self.cuelist_thread.start()
        #self.cuelist_thread.quit()
        
        self.chase_timer=QTimer(self)
        self.chase_timer.timeout.connect(self.chase_send)
        
        self.mdi = QMdiArea()
        
        ### Essential subwindows
        self.create_error_log()
        self.create_master_fader()
        
        ### Serial Monitors
        self.create_encoders()
        self.create_faders()
        self.create_keys()
        
        ### Extras
        #self.create_chase_test()
        #self.create_color()
        #self.create_xy_pad()
        
        
        self.setCentralWidget(self.mdi)
    
    ### Essential Functions
    def closeEvent(self, event):
        close = QMessageBox.question(self,"QUIT","Are you sure want to quit?",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    @pyqtSlot(bool)
    def toggle_freeze(self, toggled):
        if toggled:
            self.freezelabel.setText("Output freezed")
            output_freeze[0] = True
        else:
            self.freezelabel.setText("")
            output_freeze[0] = False
            self.abstract_thread.send_artnet_all_sock_relay()
    
    def sort(self):
        self.mdi.tileSubWindows()
    
    @pyqtSlot(int, str, object)
    def forward_cuelist_lampset(self, num, action, value):
        self.lampset.emit(num, action, value)
    
    @pyqtSlot()
    def update_error_log(self):
        self.error_text.setPlainText("\n".join(error_log_global))
        self.error_text.verticalScrollBar().setValue(self.error_text.verticalScrollBar().maximum())
    
    ## build / exec func
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
        self.mslider_resend_button=QPushButton("Resend")
        self.mslider.valueChanged.connect(self.master_sli_fader)
        self.mslider_max_button.clicked.connect(self.set_master_max)
        self.mslider_min_button.clicked.connect(self.set_master_min)
        self.mslider_resend_button.clicked.connect(self.abstract_thread.send_artnet_all_sock_relay)
        width_edit=QLineEdit()
        width_edit.setPlaceholderText(str(self.mslider.size().width()))
        height_edit=QLineEdit()
        height_edit.setPlaceholderText(str(self.mslider.size().height()))
        width_edit.returnPressed.connect(lambda: self.mslider.resize(QSize(int(width_edit.text()),self.mslider.size().height())))
        height_edit.returnPressed.connect(lambda: self.mslider.resize(QSize(self.mslider.size().width(),int(height_edit.text()))))
        master_list.append([self.mslider, 0, 0])
        master_list.append([self.mslider_max_button, 0, 1])
        master_list.append([self.mslider_min_button, 1, 1])
        master_list.append([self.mslider_resend_button, 0, 3])
        master_list.append([width_edit, 0, 2])
        master_list.append([height_edit, 1, 2])
        
        self.create_sub_area("mslider", "Master", master_list)
    
    @pyqtSlot(int)
    def master_sli_fader(self, i):
        self.master_change.emit(i)
    
    def set_master_max(self):
        self.mslider.setValue(self.mslider.maximum())
    
    def set_master_min(self):
        self.mslider.setValue(self.mslider.minimum())
    
    ### Serial Monitor Functions    
    def create_keys(self):
        keys_list=[]
        for row in range(rows):
            for col in range(cols):
                num = (row * cols) + col
                exec("self.key{0:d}=QPushButton()".format(num))
                exec("self.key{0:d}.setCheckable(True)".format(num))
                exec("keys_list.append([self.key{0:d},{1:d},{2:d}])".format(num,row,col))
        self.create_sub_area("keys", "Buttons", keys_list, width=85)
    
    def create_faders(self):
        faders_list=[]
        for fader in range(faders):
            exec("self.fader{0:d}=QLabel()".format(fader))
            exec("self.fader{0:d}.setAlignment(Qt.AlignCenter)".format(fader))
            exec("self.fader{0:d}.setText('0')".format(fader))
            exec("faders_list.append([self.fader{0:d},0,{0:d}])".format(fader))
        self.create_sub_area("faders", "Faders", faders_list, width=50)
        
    def create_encoders(self):
        encoder_list=[]
        for encoder in range(encoders):
            exec("self.encoder{0:d}=QLabel()".format(encoder))
            exec("self.encoder{0:d}.setAlignment(Qt.AlignCenter)".format(encoder))
            exec("self.encoder{0:d}.setText('0')".format(encoder))
            exec("encoder_list.append([self.encoder{0:d},0,{0:d}])".format(encoder))
        self.create_sub_area("encoders", "Encoders", encoder_list, width=30)
    
    
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
    
    ### Extra Functions
    def create_xy_pad(self):
        self.xy_pad = XY_Pad()
        self.xy_pad.position_changed.connect(self.xy_pad_sola_map)
        
        self.create_sub_area("xy_pad", "XY Pad", [[self.xy_pad,0,0]])
    
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
        
        self.create_fader("led_ma", "LED Master", chase_list, 0, 2)
        
        self.create_sub_area("chase_test", "LED Chase", chase_list, width=70)
    
    
    @pyqtSlot(int)
    def led_ma_slid_fader(self, sli):
        for i in range(110,116):
            self.lampset.emit(i, 'Dimmer', sli)
    
    @pyqtSlot(float, float)
    def xy_pad_sola_map(self, x, y):
        self.lampset.emit(100, "Pan", x*100)
        self.lampset.emit(100, "Tilt", y*100)
    
    def chase_update(self):
        temp_freq = float(self.chase_edit.text())
        self.freq = temp_freq
    
    def chase_abs_update(self):
        self.add_fac = float(self.chase_abs_edit.text())
        
    def chase_send(self):
        #for i in [110, 111, 113, 115, 114, 112]:
        i = 100
        if True:
            color_tup = colorsys.hsv_to_rgb(abs(math.sin(self.freq*time.time()+(self.add_fac*0))),1,1)#(i-110)))),1,1)
            self.lampset.emit(i,"Red",color_tup[0]*255)
            self.lampset.emit(i,"Blue",color_tup[1]*255)
            self.lampset.emit(i,"Green",color_tup[2]*255)
    
    def create_color(self):
        self.color_dia0 = QColorDialog()
        self.color_dia0.setOption(2)
        self.color_dia0.currentColorChanged.connect(self.test_colors)
        
        self.create_sub_area("color", "Color Changer", [[self.color_dia0, 0, 0]])

    @pyqtSlot(QColor)
    def test_colors(self, col):
        #for i in range(110,116):
        i=100
        if True:
            self.lampset.emit(i, 'Red', col.red())
            self.lampset.emit(i, 'Green', col.green())
            self.lampset.emit(i, 'Blue', col.blue())
    
    def faders_next_com(self):
        if GlobalVar.curr_page+1 < len(fader_map):
            next_page = GlobalVar.curr_page + 1
        else:
            next_page = 0
        for i in range(faders):
            exec("fader_map[GlobalVar.curr_page][i] = self.fader_{0:d}_ma_slid.value()".format(i))
            exec("self.fader_{0:d}_ma_slid.setValue(fader_map[next_page][i])".format(i))
            self.faderset.emit(i, fader_map[next_page][i])
            GlobalVar.curr_page = next_page
    
    
    def create_sub_area(self, name, title, wid_list, width=None):
        exec("self.{0:s}_layout = QGridLayout()".format(name))
        for wid in wid_list:
            exec("self.{0:s}_layout.addWidget(wid[0],wid[1],wid[2])".format(name))
        if width:
            exec("self.col_count=self.{0:s}_layout.columnCount()".format(name))
            for col in range(self.col_count):
                exec("self.{0:s}_layout.setColumnMinimumWidth(col,{1:d})".format(name,width))
        exec("self.{0:s}_widget = QWidget()\nself.{0:s}_widget.setLayout(self.{0:s}_layout)\nself.{0:s}_sub = QMdiSubWindow()\nself.{0:s}_sub.setWidget(self.{0:s}_widget)\nself.{0:s}_sub.setWindowTitle('{1:s}')\nself.mdi.addSubWindow(self.{0:s}_sub)\nself.{0:s}_sub.show()".format(name, title))
        #self.{0:s}_scroll=QScrollArea()\nself.{0:s}_scroll.setWidget(self.{0:s}_widget)\n
    
    def create_fader(self, name, label, liste, start, start1, fad_max=100):
        exec("self.{0:s}_slid = QSlider()\nself.{0:s}_slid.setMinimum(0)\nself.{0:s}_slid.setMaximum(fad_max)\nself.{0:s}_slid.valueChanged.connect(self.{0:s}_slid_fader)\nliste.append([QLabel('{1:s}'),start,start1])\nliste.append([self.{0:s}_slid,start+1,start1])".format(name, label))
    


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

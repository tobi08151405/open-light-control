from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import json
import time
import math
import colorsys
import types
import os
from functools import partial

import pdb

import GlobalVar
from Circular_Colorpicker import ColorPicker as NewColorPicker
from SerialThread import SerialThread
from AbstractThread import AbstractThread
from CuelistThread import CuelistThread
from XY_Pad import XY_Pad
import Create_lamps
import Reverser

path = os.getcwd()

Create_lamps.create()
Reverser.create_typ_to_func([path+"/dev/ofl-json/tao-led.json", path+"/dev/ofl-json/generic/desk-channel.json",
                             path+"/dev/ofl-json/michi.json", path+"/dev/ofl-json/stockwerk-bar.json", path+"/dev/ofl-json/stockwerk-led.json"])
Reverser.create_typ_to_addr([path+"/dev/ofl-json/tao-led.json", path+"/dev/ofl-json/generic/desk-channel.json",
                             path+"/dev/ofl-json/michi.json", path+"/dev/ofl-json/stockwerk-bar.json", path+"/dev/ofl-json/stockwerk-led.json"])
# Reverser.create_typ_to_func([path+"/dev/ofl-json/tao-led.json",path+"/dev/ofl-json/generic/desk-channel.json",path+"/dev/ofl-json/michi.json"])
# Reverser.create_typ_to_addr([path+"/dev/ofl-json/tao-led.json",path+"/dev/ofl-json/generic/desk-channel.json",path+"/dev/ofl-json/michi.json"])
#Reverser.create_typ_to_func([path+"/dev/ofl-json/generic/rgb-fader.json",path+"/dev/ofl-json/sola-wash.json"])
#Reverser.create_typ_to_addr([path+"/dev/ofl-json/generic/rgb-fader.json",path+"/dev/ofl-json/sola-wash.json"])

def change_uni(from_, to_):
    GlobalVar.uni_map[GlobalVar.uni_map_[int(from_)]] = int(to_)
    GlobalVar.uni_map_ = {v: k for k, v in GlobalVar.uni_map.items()}

class NewColorDialog(NewColorPicker):
    def __init__(self, parent=None):
        NewColorPicker.__init__(self, width=250, startupcolor=[0,255,255], parent=parent)


class ColorDialog(QColorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOptions(self.options() | QColorDialog.DontUseNativeDialog)

        for children in self.findChildren(QWidget):
            classname = children.metaObject().className()
            if classname not in ("QColorPicker", "QColorLuminancePicker"):
                children.hide()

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

        if GlobalVar.serial_enable:
            self.serial_thread = SerialThread()
            self.serial_thread.keystroke.connect(self.map_keys)
            self.serial_thread.fadermove.connect(self.map_faders)
            self.serial_thread.encodermove.connect(self.map_encoders)
            self.faderset.connect(self.serial_thread.set_fader)
            self.serial_thread.start()

        self.abstract_thread = AbstractThread()
        self.lampset.connect(self.abstract_thread.set_lamp)
        self.lampset.connect(self.set_output)
        self.master_change.connect(self.abstract_thread.dmx_thread.set_master)
        self.abstract_thread.start()

        sortact = QAction('Sort', self)
        sortact.triggered.connect(self.sort)

        quitact = QAction('Quit', self)
        quitact.setShortcut('Ctrl+Q')
        quitact.triggered.connect(self.close)

        self.freezelabel = QLabel("Output freezed")
        # self.freezelabel.setDisabled(True)

        self.freezeact = QAction('Freeze Output', self)
        self.freezeact.setCheckable(True)
        self.freezeact.toggled.connect(self.toggle_freeze)
        self.freezeact.setShortcut('Ctrl+F')
        self.freezeact.toggle()

        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('File')
        self.fileMenu.addAction(quitact)
        self.toolsMenu = self.menubar.addMenu('Tools')
        self.toolsMenu.addAction(sortact)
        self.toolsMenu.addAction(self.freezeact)
        self.windowMenu = self.menubar.addMenu('Windows')

        self.menubar.setCornerWidget(self.freezelabel)

        self.statusbar = self.statusBar()#.showMessage('Ready')
        self.statusbarhistory = QLabel()
        self.statusbarhistory.setMinimumWidth(100)
        self.statuslinebar = QLineEdit()
        self.statuslinebar.setMinimumWidth(100)
        self.statuslinebar.returnPressed.connect(self.exec_program_line)
        self.statusbar.layout().addWidget(self.statusbarhistory)
        self.statusbar.layout().addWidget(self.statuslinebar, Qt.AlignRight)
        #self.statusbar.addWidget(self.statuslinebar)
        #self.statusbar.setLayout(self.statusbar_layout)

        # self.cuelist_thread = CuelistThread()
        # self.cuelist_thread.lampset.connect(lambda x,y,z: self.lampset.emit(x, y, z))
        #self.cuelist_thread.go()
        #self.cuelist_thread.start()
        #self.cuelist_thread.quit()

        self.chase_timer=QTimer(self)
        self.chase_timer.timeout.connect(self.chase_send)

        self.mdi = QMdiArea()

        for cuelist in GlobalVar.cuelist_dict.keys():
            setattr(self,"{0:s}_cue_thread".format(cuelist),CuelistThread())
            getattr(self,"{0:s}_cue_thread".format(cuelist)).lampset.connect(self.lampset_relay)
            getattr(self,"{0:s}_cue_thread".format(cuelist)).set_cuelist(str(cuelist))

        ### Essential subwindows
        self.create_error_log()
        self.create_master_fader()
        self.create_output()

        ### Serial Monitors
        self.create_encoders()
        self.create_faders()
        self.create_keys()

        ### Extras
        self.create_chase_test()
        self.create_color()
        # self.create_color_bar()
        self.create_xy_pad()
        self.create_pb_stueck()
        # self.create_pp_stueck()

        ### Show all
        self.master_slid_sub.show()
        self.output_sub.show()
        self.stueck_sub.show()
        # self.stock_sub.show()
        self.color_sub.show()
        # self.color1_sub.show()

        self.setCentralWidget(self.mdi)
        #pdb.set_trace()
        # self.change_led()

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
            GlobalVar.output_freeze[0] = True
        else:
            self.freezelabel.setText("")
            GLobalVar.output_freeze[0] = False
            self.abstract_thread.send_artnet_all_sock_relay()

    def sort(self):
        self.mdi.tileSubWindows()

    @pyqtSlot()
    def update_error_log(self):
        self.error_text.setPlainText("\n".join(GlobalVar.error_log_global))
        self.error_text.verticalScrollBar().setValue(self.error_text.verticalScrollBar().maximum())

    # @pyqtSlot(str)
    def key_pressed(self, key, pressed=True):
        try:
            if pressed:
                if GlobalVar.key_mapping[key][0] == "pad":
                    if GlobalVar.key_mapping.get(key,["",False])[3]:
                        self.statuslinebar.insert(
                            GlobalVar.key_mapping.get(key, [""])[2])
                    else:
                        if GlobalVar.key_mapping.get(key, [""])[2] == "Enter":
                            self.statuslinebar.returnPressed.emit()
                elif GlobalVar.key_mapping[key][0] == "cuelist":
                    if GlobalVar.key_mapping[key][2] == "go":
                        self.cuelist_go(getattr(self, "{0:s}_cue_thread)".format(
                            GlobalVar.key_mapping[key][1])))
                elif GlobalVar.key_mapping[key][0] == "command":
                    getattr(self, GlobalVar.key_mapping[key][1])()
                else:
                    raise(KeyError)
        except:
            GlobalVar.error_log_global.append("Key press failed: num {0:s}".format(key))

    def exec_program_line(self):
        text = self.statuslinebar.text()
        clear=False
        try:
            if "/" in text:
                nums=text.split("*")[0].split("c")[0]
                number=nums.split("/")
                numbers="+".join([str(x) for x in range(int(number[0]),int(number[1])+1)])
                text=numbers+text[text.index(nums)+len(nums):]
        except:
            GlobalVar.error_log_global.append(
                "Programmer Error: unkown command")
        if "*" in text:
            try:
                dims = text.split("*")[1]
                if len(text.split("*")) == 3:
                    dim = 100
                elif dims == "":
                    dim = 0
                    clear = True
                elif dims == "0":
                    dim = int(dims)
                else:
                    dim = int(dims)
                    if dim > 100:
                        raise ValueError
            except ValueError:
                GlobalVar.error_log_global.append("Programmer Error: value out of range")
                self.statuslinebar.clear()
                return
            if text.split("*")[0] == "":
                lamps = self.statusbarhistory.text()
            else:
                lamps = text.split("*")[0]
            if "+" in lamps:
                lamp = lamps.split("+")
            else:
                lamp = [lamps]
            for i in lamp:
                if clear:
                    try:
                        GlobalVar.in_use_programmer.pop(i)
                    except KeyError:
                        pass
                else:
                    GlobalVar.in_use_programmer[i] = dim
                self.lampset.emit(int(i),"Dimmer",dim)
        elif "c" in text:
            if "+" in text.split("c")[0]:
                lamp = text.split("c")[0].split("+")
            else:
                lamp = [text.split("c")[0]]
            value = text.split("c")[1]
            if "r" in value:
                setting = "Red"
                set_value = int(value.split("r")[1])
            elif "g" in value:
                setting = "Green"
                set_value = int(value.split("g")[1])
            elif "b" in value:
                setting = "Blue"
                set_value = int(value.split("b")[1])
            else:
                setting = "Color"
                set_value = value.replace("(","").replace(")","").split(",")
            if setting == "Color":
                for i in lamp:
                    try:
                        dim = GlobalVar.in_use_programmer[i]
                    except KeyError:
                        dim = 0
                    GlobalVar.in_use_programmer[i] = dim
                    self.lampset.emit(int(i),"Red",int(set_value[0]))
                    self.lampset.emit(int(i),"Green",int(set_value[1]))
                    self.lampset.emit(int(i),"Blue",int(set_value[2]))
            else:
                for i in lamp:
                    try:
                        dim = GlobalVar.in_use_programmer[i]
                    except KeyError:
                        dim = 0
                    GlobalVar.in_use_programmer[i] = dim
                    self.lampset.emit(int(i),setting,set_value)
        else:
            GlobalVar.error_log_global.append("Programmer Error: unkown command")
        self.statusbarhistory.setText("+".join(GlobalVar.in_use_programmer.keys()))
        self.statuslinebar.clear()

    ## build / exec func
    def create_error_log(self):
        self.error_text = QTextEdit()
        self.error_text.setReadOnly(1)
        self.create_sub_area("error", "Error Log", [[self.error_text, 0, 0]])

    def create_output(self):
        self.output_layout = QGridLayout()
        self.output_layout.addWidget(QLabel("Num"),0,0)
        self.output_layout.addWidget(QLabel("Dimmer"),0,1)
        self.output_layout.addWidget(QLabel("Color"),0,2)
        # self.output_layout.addWidget(QLabel("Gobo"),0,3)
        # self.output_layout.addWidget(QLabel("Pan"),0,4)
        # self.output_layout.addWidget(QLabel("Tilt"),0,5)
        line=1
        for num in list(GlobalVar.nr_to_typ.keys()):
            self.output_layout.addWidget(QLabel(str(num)),line,0)
            if GlobalVar.typ_to_func[GlobalVar.nr_to_typ[num]]['Dimmer']:
                setattr(self,"output_{0:d}_Dimmer".format(num),QLabel('0'))
                self.output_layout.addWidget(getattr(self,"output_{0:d}_Dimmer".format(num)),line,1)
            if not GlobalVar.typ_to_func[GlobalVar.nr_to_typ[num]]['Color'] == False:
                setattr(self,"output_{0:d}_Color".format(num),QLabel('(0,0,0)'))
                self.output_layout.addWidget(getattr(self,"output_{0:d}_Color".format(num)),line,2)
            # if not GlobalVar.typ_to_func[GlobalVar.nr_to_typ[num]]['Gobo'] == False:
            #     setattr(self,"output_{0:d}_Gobo".format(num),QLabel('Open'))
            #     self.output_layout.addWidget(getattr(self,"output_{0:d}_Gobo".format(num)),line,3)
            # if not GlobalVar.typ_to_func[GlobalVar.nr_to_typ[num]]['Pan'] == False:
            #     setattr(self,"output_{0:d}_Pan".format(num),QLabel('Open'))
            #     self.output_layout.addWidget(getattr(self,"output_{0:d}_Pan".format(num)),line,4)
            # if not GlobalVar.typ_to_func[GlobalVar.nr_to_typ[num]]['Tilt'] == False:
            #     setattr(self,"output_{0:d}_Tilt".format(num),QLabel('Open'))
            #     self.output_layout.addWidget(getattr(self,"output_{0:d}_Tilt".format(num)),line,4)
            line+=1

        col_count=self.output_layout.columnCount()
        for col in range(col_count):
            self.output_layout.setColumnMinimumWidth(col,70)
        self.output_layout.setColumnMinimumWidth(2,100)

        self.output_widget = QWidget()
        self.output_widget.setLayout(self.output_layout)
        self.output_scroll=QScrollArea()
        self.output_scroll.setWidget(self.output_widget)
        self.output_sub = QMdiSubWindow()
        self.output_sub.setWidget(self.output_scroll)
        self.output_sub.setWindowTitle('Output')
        self.output_sub.setFont(QFont('Sans Serif', 10))
        self.mdi.addSubWindow(self.output_sub)

    @pyqtSlot(int, str, object)
    def set_output(self, num, setting, value):
        try:
            if any(setting == x for x in ["Red", "Green", "Blue"]):
                self.text=getattr(self,"output_{0:d}_Color".format(num)).text()
                text=self.text.replace("(","")
                text=text.replace(")","")
                text=text.split(",")
                if setting == "Red":
                    text[0]=str(round(value,1))
                elif setting == "Green":
                    text[1]=str(round(value,1))
                elif setting == "Blue":
                    text[2]=str(round(value,1))
                getattr(self,"output_{0:d}_Color".format(num)).setText("("+",".join(text)+")")
            else:
                getattr(self,"output_{0:d}_{1:s}".format(num,setting)).setText(str(value))
        except:
            pass

    def create_master_fader(self):
        master_list = []

        self.master_slid=QSlider()
        self.master_slid.setMinimum(0)
        self.master_slid.setMaximum(100)
        self.master_slid.setStyleSheet(GlobalVar.slider_stylesheet)
        self.master_slid_max_button=QPushButton("Max")
        self.master_slid_min_button=QPushButton("Min")
        self.master_slid_resend_button=QPushButton("Resend")
        self.master_slid.valueChanged.connect(self.master_slid_fader)
        self.master_slid_max_button.clicked.connect(self.set_master_max)
        self.master_slid_min_button.clicked.connect(self.set_master_min)
        self.master_slid_resend_button.clicked.connect(self.abstract_thread.send_artnet_all_sock_relay)
        width_edit=QLineEdit()
        width_edit.setPlaceholderText(str(self.master_slid.size().width()))
        height_edit=QLineEdit()
        height_edit.setPlaceholderText(str(self.master_slid.size().height()))
        width_edit.returnPressed.connect(lambda: self.master_slid.resize(QSize(int(width_edit.text()),self.master_slid.size().height())))
        height_edit.returnPressed.connect(lambda: self.master_slid.resize(QSize(self.master_slid.size().width(),int(height_edit.text()))))
        master_list.append([self.master_slid, 0, 0, 2, 1])
        master_list.append([self.master_slid_max_button, 0, 1])
        master_list.append([self.master_slid_min_button, 1, 1])
        master_list.append([self.master_slid_resend_button, 0, 3])
        master_list.append([width_edit, 0, 2])
        master_list.append([height_edit, 1, 2])

        self.create_sub_area("master_slid", "Master", master_list)

    @pyqtSlot(int)
    def master_slid_fader(self, i):
        self.master_change.emit(i)

    def set_master_max(self):
        self.master_slid.setValue(self.master_slid.maximum())

    def set_master_min(self):
        self.master_slid.setValue(self.master_slid.minimum())

    ### Serial Monitor Functions
    def create_keys(self):
        keys_list=[]
        for row in range(GlobalVar.rows):
            for col in range(GlobalVar.cols):
                num = (row * GlobalVar.cols) + col
                setattr(self, "key"+str(num),
                        QPushButton(GlobalVar.key_mapping.get(str(num), ["", "None"])[1]))
                # getattr(self,"keys"+str(num)).setCheckable(True)
                getattr(self,"key"+str(num)).setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
                getattr(self,"key"+str(num)).pressed.connect(partial(self.key_pressed, str(num)))
                keys_list.append([getattr(self,"key"+str(num)),row,col])
        self.create_sub_area("keys", "Buttons", keys_list, width=85)

    def create_faders(self):
        faders_list=[]
        for fader in range(GlobalVar.faders):
            setattr(self,"fader"+str(fader),QLabel())
            getattr(self,"fader"+str(fader)).setAlignment(Qt.AlignCenter)
            getattr(self,"fader"+str(fader)).setText('0')
            faders_list.append([getattr(self,"fader"+str(fader)),0,fader])
        self.create_sub_area("faders", "Faders", faders_list, width=50)

    def create_encoders(self):
        encoder_list=[]
        for encoder in range(GlobalVar.encoders):
            setattr(self,"encoder"+str(encoder),QLabel())
            getattr(self,"encoder"+str(encoder)).setAlignment(Qt.AlignCenter)
            getattr(self,"encoder"+str(encoder)).setText('0')
            encoder_list.append([getattr(self,"encoder"+str(encoder)),0,encoder])
        self.create_sub_area("encoders", "Encoders", encoder_list, width=30)


    @pyqtSlot(str, bool)
    def map_keys(self, key, pressed):
        try:
            self.key_pressed(key,pressed)
        except NameError:
            print("button {0:s} not found!".format(key))

    @pyqtSlot(str, int)
    def map_faders(self, fader, value):
        try:
            fader_to_set = GlobalVar.fader_mapping[fader]+"_slid"
            getattr(self,fader_to_set).setValue((value/1023)*getattr(self,fader_to_set).maximum())
        except KeyError:
            pass

    @pyqtSlot(str, int)
    def map_encoders(self, encoder, value):
        try:
            cur = int(getattr(self,"encoder"+encoder).text())
            getattr(self,"encoder"+encoder).setText(str(cur-value))
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
        for i in [110, 111, 113, 115, 114, 112]:
        #i = 100
        #if True:
            color_tup = colorsys.hsv_to_rgb(abs(math.sin(self.freq*time.time()+(self.add_fac*(i-110)))),1,1)#0))),1,1)
            self.lampset.emit(i,"Red",color_tup[0]*255)
            self.lampset.emit(i,"Blue",color_tup[1]*255)
            self.lampset.emit(i,"Green",color_tup[2]*255)

    def create_color(self):
        self.color_dia0 = NewColorDialog(parent=self)
        # self.color_dia0.setOption(2)
        self.color_dia0.currentColorChanged.connect(self.test_colors)

        self.create_sub_area("color", "Color Changer LED", [[self.color_dia0, 0, 0]])

    def create_color_bar(self):
        self.color_dia1 = ColorDialog(parent=self)
        # self.color_dia0.setOption(2)
        self.color_dia1.currentColorChanged.connect(self.test_colors1)

        self.create_sub_area("color1", "Color Changer Bar", [[self.color_dia1, 0, 0]])

    @pyqtSlot(QColor)
    def test_colors(self, col):
        for i in range(110,116):#110,116
        #i=100
        #if True:
            self.lampset.emit(i, 'Red', col.red())
            self.lampset.emit(i, 'Green', col.green())
            self.lampset.emit(i, 'Blue', col.blue())

    @pyqtSlot(QColor)
    def test_colors1(self, col):
        for i in range(20,22):
        #i=100
        #if True:
            self.lampset.emit(i, 'Red', col.red())
            self.lampset.emit(i, 'Green', col.green())
            self.lampset.emit(i, 'Blue', col.blue())

    def faders_next_com(self):
        if GlobalVar.curr_page+1 < len(GlobalVar.fader_map):
            next_page = GlobalVar.curr_page + 1
        else:
            next_page = 0
        for i in range(GlobalVar.faders):
            GlobalVar.fader_map[GlobalVar.curr_page][i] = getattr(
                self, "fader_{0:d}_ma_slid".format(i)).value()
            getattr(self, "fader_{0:d}_ma_slid".format(i)).setValue(
                GlobalVar.fader_map[next_page][i])
            self.faderset.emit(i, GlobalVar.fader_map[next_page][i])
            GlobalVar.curr_page = next_page

    def create_pb_stueck(self):
        stueck_list = []

        self.create_fader("pub", "Pub", stueck_list, 0, 0)
        self.create_fader("back", "Backlight", stueck_list, 0, 1)
        self.create_fader("grund", "Grundlicht", stueck_list, 0, 2)
        self.create_fader("spot", "Spot", stueck_list, 0, 3)

        self.create_sub_area("stueck", "PB Stück", stueck_list, width=70)

    @pyqtSlot(int)
    def pub_slid_fader(self, i):
        self.lampset.emit(10, "Dimmer", i)
        self.lampset.emit(19, "Dimmer", i)
        self.lampset.emit(7, "Dimmer", i)

    @pyqtSlot(int)
    def back_slid_fader(self, i):
        self.lampset.emit(44, "Dimmer", i)

    @pyqtSlot(int)
    def grund_slid_fader(self, i):
        self.lampset.emit(22, "Dimmer", i)
        self.lampset.emit(21, "Dimmer", i)
        self.lampset.emit(17, "Dimmer", i)
        self.lampset.emit(14, "Dimmer", i)

    @pyqtSlot(int)
    def spot_slid_fader(self, i):
        self.lampset.emit(18, "Dimmer", i)

    def create_pp_stueck(self):
        stock_list = []

        self.create_fader("L", "L", stock_list, 0, 0)
        self.create_fader("R", "R", stock_list, 0, 1)
        self.create_fader("led_d", "LED Dim", stock_list, 0, 2)
        self.create_fader("bar_d", "Bar Dim R", stock_list, 0, 3)

        self.create_sub_area("stock", "PP Stück", stock_list, width=70)

    @pyqtSlot(int)
    def L_slid_fader(self, i):
        self.lampset.emit(1, "Dimmer", i)

    @pyqtSlot(int)
    def R_slid_fader(self, i):
        self.lampset.emit(2, "Dimmer", i)

    @pyqtSlot(int)
    def led_d_slid_fader(self, i):
        self.lampset.emit(10, "Dimmer", i)

    @pyqtSlot(int)
    def bar_d_slid_fader(self, i):
        self.lampset.emit(20, "Dimmer", i)
        self.lampset.emit(21, "Dimmer", i)

    def create_sub_area(self, name, title, wid_list, width=None):
        setattr(self,name+"_layout",QGridLayout())
        for wid in wid_list:
            if len(wid) == 3:
                wid.append(1)
                wid.append(1)
            getattr(self,name+"_layout").addWidget(wid[0],wid[1],wid[2],wid[3],wid[4])
        if width:
            self.col_count=getattr(self,name+"_layout").columnCount()
            for col in range(self.col_count):
                getattr(self,name+"_layout").setColumnMinimumWidth(col,width)
        setattr(self,name+"_widget",QWidget())
        getattr(self,name+"_widget").setLayout(getattr(self,name+"_layout"))
        setattr(self,name+"_sub",QMdiSubWindow())
        getattr(self,name+"_sub").setWidget(getattr(self,name+"_widget"))
        getattr(self,name+"_sub").setWindowTitle(title)
        self.mdi.addSubWindow(getattr(self,name+"_sub"))
        getattr(self,name+"_sub").hide()
        setattr(self,name+"act",QAction(title, self))
        getattr(self,name+"act").triggered.connect(lambda: getattr(self,name+"_sub").show())
        self.windowMenu.addAction(getattr(self,name+"act"))

        # setattr(self,name+"_scroll",QScrollArea())
        # getattr(self,name+"_scroll").setWidget(getattr(self,name+"_widget"))

    def create_fader(self, name, label, liste, start, start1, fad_max=100):
        setattr(self,name+"_slid",QSlider())
        getattr(self,name+"_slid").setMinimumHeight(200)
        getattr(self, name+"_slid").setStyleSheet(GlobalVar.slider_stylesheet)
        getattr(self,name+"_slid").setMinimum(0)
        getattr(self,name+"_slid").setMaximum(fad_max)
        getattr(self,name+"_slid").valueChanged.connect(getattr(self,name+"_slid_fader"))
        liste.append([QLabel(label),start,start1])
        liste.append([getattr(self,name+"_slid"),start+1,start1])

    @pyqtSlot(int, str, object)
    def lampset_relay(self, x, y, z):
        self.lampset.emit(x, y, z)

    def cuelist_go(self, cuelist):
        if cuelist.isRunning():
            cuelist.go()
        else:
            cuelist.start()

    def unset_pub(self):
        if GlobalVar.fader_mapping["2"] == "pub":
            GlobalVar.fader_mapping["2"] = "spot"
        else:
            GlobalVar.fader_mapping["2"] = "pub"

    def change_led(self):
        self.lampset.emit(10, "Red", 255)
        self.lampset.emit(10, "Green", 191)
        self.lampset.emit(10, "Blue", 62)
        self.lampset.emit(11, "Red", 255)
        self.lampset.emit(20, "Red", 255)
        self.lampset.emit(20, "Green", 147)
        self.lampset.emit(20, "Blue", 52)
        self.lampset.emit(21, "Red", 255)
        self.lampset.emit(21, "Green", 147)
        self.lampset.emit(21, "Blue", 52)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    # pdb.set_trace()
    sys.exit(app.exec_())

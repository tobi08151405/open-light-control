from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import struct
import socket

from GlobalVar import universe_num, uni_map

class DmxThread(QThread):
    
    def __init__(self):
        QThread.__init__(self)
        
        self.uni_list = []
        for i in range(universe_num):
            self.uni_list.append([])
        
        for uni in self.uni_list:
            for i in range(512):
                uni.append(0)
        
        self.artnet_prefix = bytearray([0x41, 0x72, 0x74, 0x2d, 0x4e, 0x65, 0x74, 0x00, 0x00, 0x50, 0x00, 0x0e, 0x00, 0x00])
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b'enp5s0')
        self.sock.settimeout(5)
        self.artnet_timer = QTimer(self)
        self.artnet_timer.timeout.connect(self.send_artnet_all)
        self.artnet_timer.start(4000)
    
    def run(self):
        loop = QEventLoop()
        loop.exec_()
    
    def send_artnet_all(self):
        for uni in range(universe_num):
            self.send_artnet(uni)
    
    def send_artnet(self, uni):
        packet = self.artnet_prefix.copy()
        packet+=struct.pack("<h", uni_map[uni])+struct.pack(">h", 512)
        for chan in self.uni_list[uni]:
            packet+=struct.pack("B", chan)
        self.sock.sendto(packet, ('255.255.255.255', 6454))
    
    @pyqtSlot()
    def add_universe(self):
        universe_num += 1
        self.uni_list.append([])
        for i in range(512):
            self.uni_list[-1].append(0)
    
    @pyqtSlot(int, int, int)
    def set_channel(self, universe, channel, value):
        self.uni_list[universe][channel] = int(value)
        self.send_artnet(universe)

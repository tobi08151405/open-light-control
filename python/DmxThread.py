from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, QTimer, QEventLoop, pyqtSlot
from PyQt5.QtGui import *

import struct
import socket

from GlobalVar import universe_num, uni_map, output_freeze, error_log_global


class DmxThread(QThread):
    master_val = 0

    def __init__(self):
        QThread.__init__(self)

        self.uni_list = []
        self.output_last = []
        for i in range(universe_num):
            self.uni_list.append([])
            self.output_last.append([])

        for uni in self.uni_list:
            for i in range(512):
                uni.append(0)

        self.artnet_prefix = bytearray(
            [0x41, 0x72, 0x74, 0x2d, 0x4e, 0x65, 0x74, 0x00, 0x00, 0x50, 0x00, 0x0e, 0x00, 0x00])

        self.sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, True)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b'eth0')
        self.sock.settimeout(5)
        self.artnet_timer = QTimer(self)
        self.artnet_timer.timeout.connect(self.send_artnet_all)
        self.artnet_timer.start(4000)
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.update_output)
        self.global_timer.start(20)

    def run(self):
        loop = QEventLoop()
        loop.exec_()

    def update_output(self):
        # print(self.output_last == self.uni_list)
        if not self.output_last == self.uni_list:
            self.send_artnet_all()
            for i in range(len(self.uni_list)):
                self.output_last[i] = self.uni_list[i].copy()
            # self.output_last = self.uni_list.copy()

    def send_artnet_all(self):
        for uni in range(universe_num):
            self.send_artnet(uni)

    def send_artnet(self, uni):
        if not output_freeze[0]:
            packet = self.artnet_prefix.copy()
            packet += struct.pack("<h", uni_map[uni])+struct.pack(">h", 512)
            for chan in self.uni_list[uni]:
                packet += struct.pack("B", int(chan*self.master_val))
            try:
                self.sock.sendto(packet, ('255.255.255.255', 6454))
            except OSError:
                print("DmxThread: Network not reachable")
                error_log_global.append("DmxThread: Network not reachable")

    @pyqtSlot()
    def add_universe(self):
        universe_num += 1
        self.uni_list.append([])
        self.output_last.append([])
        for i in range(512):
            self.uni_list[-1].append(0)

    @pyqtSlot(int, int, int)
    def set_channel(self, universe, channel, value):
        self.uni_list[universe][channel] = int(value)
        # self.send_artnet(universe)

    @pyqtSlot(int)
    def set_master(self, ma):
        self.master_val = ma/100
        self.send_artnet_all()

    @pyqtSlot()
    def send_artnet_all_sock(self):
        self.send_artnet_all()

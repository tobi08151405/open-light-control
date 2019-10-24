from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from GlobVar import *

class CuelistThread(QThread):
    cur_pos = 0
    cuelist = {
        0: [[35, 'Intensity', 100], [40, 'Intensity', 100]],
        1: []
        }
    
    def __init__(self):
        QThread.__init__(self)
        
    def run(self):
        loop = QEventLoop()
        loop.exec_()
    
    @pyqtSlot()
    def _go(self):
        pass
    
    #def 

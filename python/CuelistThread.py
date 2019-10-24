from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from GlobVar import *

class CuelistThread(QThread):
    
    def __init__(self):
        QThread.__init__(self)
        
    def run(self):
        pass
    
    @pyqtSlot()
    def _go(self):
        pass

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt

class XY_Pad(QWidget):
    position_changed = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        super(XY_Pad, self).__init__(parent)
        self.on_wid = False
        self.p = self.palette()
        self.p.setColor(self.backgroundRole(), Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(self.p)
        self.setMinimumHeight(300)
        self.setMinimumWidth(300)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.on_wid = True

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.on_wid:
            x = event.pos().x()
            y = event.pos().y()
            height = self.size().height()
            width = self.size().width()
            if ((x >= 0) and (y >= 0)) and ((x <= width) and y <= height):
                self.position_changed.emit(x/width,y/height)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.on_wid:
            x = event.pos().x()
            y = event.pos().y()
            height = self.size().height()
            width = self.size().width()
            if ((x >= 0) and (y >= 0)) and ((x <= width) and y <= height):
                self.position_changed.emit(x/width,y/height)
            self.on_wid = False

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen
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
        self.x = -1
        self.y = -1
        self.height = self.size().height()
        self.width = self.size().width()
        self.setMouseTracking(True)

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        self.MouseDraw(qp)
        qp.end()

    def MouseDraw(self, qp):
        pen= QPen(Qt.red, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(self.x,0,self.x,self.height)
        qp.drawLine(0,self.y,self.width,self.y)

    def drawLines(self, qp):
        pen = QPen(Qt.lightGray, 2, Qt.SolidLine)
        qp.setPen(pen)
        size=self.size()
        qp.drawLine(0, size.height()/2, size.width(), size.height()/2)
        qp.drawLine(size.width()/2, 0, size.width()/2, size.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.on_wid = True

    def mouseMoveEvent(self, event):
        self.x = event.pos().x()
        self.y = event.pos().y()
        self.height = self.size().height()
        self.width = self.size().width()
        if (event.buttons() & Qt.LeftButton) and self.on_wid:
            if ((self.x >= 0) and (self.y >= 0)) and ((self.x <= self.width) and self.y <= self.height):
                self.position_changed.emit(self.x/self.width,self.y/self.height)
        self.update()

    def mouseReleaseEvent(self, event):
        self.x = event.pos().x()
        self.y = event.pos().y()
        self.height = self.size().height()
        self.width = self.size().width()
        if event.button() == Qt.LeftButton and self.on_wid:
            if ((self.x >= 0) and (self.y >= 0)) and ((self.x <= self.width) and self.y <= self.height):
                self.position_changed.emit(self.x/self.width,self.y/self.height)
            self.on_wid = False

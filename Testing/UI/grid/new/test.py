from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

class Drew(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setGeometry(0,0,100,100)

	def paintEvent(self, e):
		painter = QtGui.QPainter(self)
		brush = QtGui.QBrush()
		pen = QtGui.QPen(QtGui.QColor('blue'),3)
		painter.setPen(pen)
		size = self.size()
		painter.drawLine(size.width()/2, size.height(), size.width()/2, 2*size.height()/3)

		painter.drawLine(0, size.height()/2, size.width()/3, size.height()/2)
		painter.drawArc(size.width()/6, size.height()/2, size.width()/3, size.height()/3, 0,90*16)

app = QtWidgets.QApplication([])
d = Drew()
d.show()
app.exec_()
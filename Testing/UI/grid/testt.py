import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPainter, QColor, QFont

class Drew(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.paintEvent("")

	def paintEvent(self, e):
		painter = QtGui.QPainter(self)
		brush = QtGui.QBrush()
		pen = QtGui.QPen(QtGui.QColor('blue'),3)
		painter.setPen(pen)
		size = self.size()
		painter.drawLine(size.width()/2, size.height(), size.width()/2, 2*size.height()/3)

		painter.drawLine(0, size.height()/2, size.width()/3, size.height()/2)
		painter.drawArc(size.width()/6, size.height()/2, size.width()/3, size.height()/3, 0,90*16)

class IndicSelectWindow(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(IndicSelectWindow, self).__init__(parent=parent)
		self.resize(500, 400)
		self.layout = QtWidgets.QHBoxLayout(self)
		self.scrollArea = QtWidgets.QScrollArea(self)
		self.scrollArea.setWidgetResizable(True)
		self.scrollAreaWidgetContents = QtWidgets.QWidget()
		self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
		self.scrollArea.setWidget(self.scrollAreaWidgetContents)
		self.layout.addWidget(self.scrollArea)

		for i in range(100):
			for j in range(5):
				# QtWidgets.QPushButton()
				self.gridLayout.addWidget(Drew(), i, j)

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	w = IndicSelectWindow()
	w.show()
	sys.exit(app.exec_())
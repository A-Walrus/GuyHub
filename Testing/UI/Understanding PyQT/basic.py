import sys
from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication, 
                             QScrollArea,QMainWindow, QLabel,QSizePolicy)
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize , QPointF
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QColor, QFont,QPen


class Cell(QWidget):
	def __init__(self):
		super().__init__()
		self.initUI()


	def initUI(self):
		self.setFixedSize(20,20)

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		qp.setPen(QPen(QColor('blue'),2))
		qp.drawLine(10, 0,10,20) # up and down
		qp.drawLine(0, 10,20,10) # left right
		qp.setBrush(QColor('blue'))
		qp.drawEllipse(QPointF(10,10),3,3)
		qp.end()




class Example(QMainWindow):

	def __init__(self):
		super().__init__()
		self.initUI()


	def initUI(self):
		self.setGeometry(300, 300, 300, 220)
		self.setWindowTitle('Tree')

		self.scroll = QScrollArea()
		self.widget = QWidget()

		self.vbox = QVBoxLayout()
		self.vbox.setSpacing(0)

		for i in range(10):
			hbox = QHBoxLayout()
			widget = QWidget()
			
			
			label = QLabel('Commit Name')
			label.setAlignment(Qt.AlignRight)
			label.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed))
			for i in range(5):
				btn = Cell()
				btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
				hbox.addWidget(btn)
			hbox.addWidget(label)
			hbox.setContentsMargins(0, 0, 0, 0)
			hbox.setSpacing(0)

			widget.setLayout(hbox)
			widget.setFixedHeight(20)

			self.vbox.addWidget(widget)
		self.vbox.addWidget(QWidget())
		self.widget.setLayout(self.vbox)
		self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scroll.setWidgetResizable(True)
		self.scroll.setWidget(self.widget)
		self.setCentralWidget(self.scroll)
		self.show()



def main():

    app = QApplication(sys.argv)

    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
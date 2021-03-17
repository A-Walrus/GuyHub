import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

SIZE = 20

class Info():
	def __init__(self,dot,end,color):
		self.dot = dot
		self.end = end
		self.color = color

class Cell(QWidget):
	def __init__(self,infos):
		super().__init__()
		self.initUI()
		self.infos = infos


	def initUI(self):
		self.setFixedSize(SIZE,SIZE)

	def paintEvent(self, event):
		qp = QPainter()
		qp.begin(self)
		for info in self.infos:
			qp.setPen(QPen(info.color,2))
			if not info.end:
				qp.drawLine(SIZE/2, 0,SIZE/2,SIZE) # up and down
			else:
				qp.drawLine(SIZE/2, SIZE,SIZE/2,SIZE/2) # up and down
			# qp.drawLine(0, SIZE/2,SIZE,SIZE/2) # left right
			if info.dot:
				qp.setBrush(info.color)
				qp.drawEllipse(QPointF(SIZE/2,SIZE/2),3,3)
		qp.end()




class Tree(QScrollArea):
	def __init__(self,commits,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.commits= commits
		self.initUI()


	def initUI(self):
		self.widget = QWidget()

		self.vbox = QVBoxLayout()
		self.vbox.setSpacing(0)

		for i in self.commits:
			hbox = QHBoxLayout()
			widget = QWidget()
			
			
			label = QLabel('Commit Name')
			label.setAlignment(Qt.AlignRight)
			label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
			for j in range(5):
				if j%2==0:
					btn = Cell([Info(True,False,QColor('blue'))])
				else:
					btn = Cell([Info(True,True,QColor('red'))])
				btn.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
				hbox.addWidget(btn)
			hbox.addWidget(label)
			hbox.setContentsMargins(0, 0, 0, 0)
			hbox.setSpacing(0)

			widget.setLayout(hbox)
			widget.setFixedHeight(SIZE)

			self.vbox.addWidget(widget)
		self.vbox.addWidget(QWidget())
		self.widget.setLayout(self.vbox)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidgetResizable(True)
		self.setWidget(self.widget)
		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))


def main():

    app = QApplication(sys.argv)
    win = QWidget()
    vbox = QVBoxLayout()
    tree = Tree([])

    vbox.addWidget(tree)
    vbox.addWidget(QPushButton('button'))
    win.setLayout(vbox)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
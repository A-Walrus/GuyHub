from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

sys.path.append(r'D:\Users\Guy\School\cyber\GuyHub\General')
from classes import *

sys.path.append(r'D:\Users\Guy\School\cyber\GuyHub\Server')
import Database

SIZE = 30

class Info():
	def __init__(self,dot,dirs,color):
		self.dot = dot
		self.dirs = dirs
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

			if info.dirs[0]:
				qp.drawLine(SIZE/2, SIZE/3,SIZE/2,0) # up and down
			if info.dirs[1]:
				qp.drawLine(2*SIZE/3, SIZE/2,SIZE,SIZE/2) # up and down
			if info.dirs[2]:
				qp.drawLine(SIZE/2, 2*SIZE/3,SIZE/2,SIZE) # up and down
			if info.dirs[3]:
				qp.drawLine(SIZE/3, SIZE/2,0,SIZE/2) # up and down
			# qp.drawLine(0, SIZE/2,SIZE,SIZE/2) # left right
			if info.dirs[3] and info.dirs[2]:
				qp.drawArc(SIZE/6,SIZE/2,SIZE/3,SIZE/3,0,90*16) # top arc
			if info.dirs[3] and info.dirs[0]:
				qp.drawArc(SIZE/6,SIZE/6,SIZE/3,SIZE/3,0,-90*16) # bottom arc

			if info.dirs[3] and info.dirs[1]:
				qp.drawLine(SIZE, SIZE/2,0,SIZE/2)

			if info.dirs[2] and info.dirs[0]:
				qp.drawLine(SIZE/2, SIZE,SIZE/2,0)

			if info.dot:
				qp.setBrush(info.color)
				qp.drawEllipse(QPointF(SIZE/2,SIZE/2),3,3)
				
		qp.end()




class Tree(QScrollArea):
	def __init__(self,commits,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.COLORS = ['blue','green','red','yellow']
		self.commits= commits
		self.initUI()


	def initUI(self):
		self.widget = QWidget()

		self.vbox = QVBoxLayout()
		self.vbox.setSpacing(0)

		branches = []
		grid = [[] for i in self.commits]
		for i, commit in enumerate(self.commits):
			new_branch = False
			if not commit.branch in branches:
				branches.append(commit.branch)
				new_branch=True
			for j in branches:
				grid[i].append(Cell([]))

			index = branches.index(commit.branch)
			
			root = new_branch and commit.branch =='Main'
			end_of_branch = commit.idd == max([commit.idd for commit in filter(lambda x: x.branch == commit.branch,self.commits)])
			for j,b in enumerate(branches):
				if b ==None:
					grid[i][j] = Cell([])
				elif b == commit.branch:
					grid[i][j] = Cell([Info(True,[not root,False,not end_of_branch,False],QColor(self.COLORS[j]))])
					if end_of_branch:
						branches[index]=None
				else:
					grid[i][j] = Cell([Info(False,[True,False,True,False],QColor(self.COLORS[j]))])
		for i in range(len(self.commits)):
			hbox = QHBoxLayout()
			widget = QWidget()
			
			
			label = QLabel(self.commits[i].name)
			label.setAlignment(Qt.AlignRight)
			label.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
			for cell in grid[i]:
				hbox.addWidget(cell)
			spacer = QWidget()
			spacer.setFixedWidth(20)
			hbox.addWidget(spacer)
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

	db = Database.Db(r"D:\Users\Guy\School\cyber\GuyHub\Server\GuyHub.db")
	a = db.get_commits("Repos.id=1")

	tree = Tree(a)

	vbox.addWidget(tree)
	vbox.addWidget(QPushButton('button'))
	win.setLayout(vbox)
	win.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
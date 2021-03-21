from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
from http.client import HTTPConnection

SIZE = 24

class Cell(QWidget):
	def __init__(self,infos,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.infos = infos
		self.setFixedSize(SIZE,SIZE)

	def drawBase(self,event):
		super().paintEvent(event)
		opt = QStyleOption()
		opt.initFrom(self)
		p = QPainter(self)
		s = self.style()
		s.drawPrimitive(QStyle.PE_Widget, opt, p, self) 

	def paintEvent(self, event):
		self.drawBase(event)

		qp = QPainter()
		qp.begin(self)
		qp.setRenderHint(QPainter.Antialiasing)
		for info in self.infos[::-1]:
			qp.setPen(QPen(QColor(info["color"]),2))
			for direction in set(info["dirs"]):
				pattern = [1,2,1,-2]
				qp.drawLine(SIZE/2,SIZE/2,(SIZE/2)*pattern[direction],(SIZE/2)*pattern[(direction-1)%4])
			if "symbol" in info:
				qp.setBrush(QColor(info["color"]))
				if info["symbol"]=="dot":
					qp.drawEllipse(QPointF(SIZE/2,SIZE/2),3,3)
				if info["symbol"]=="merge":
					offset = 6
					qp.drawPolygon(	QPointF(SIZE/2-offset,SIZE/2),
									QPointF(SIZE/2,SIZE/2+offset),
									QPointF(SIZE/2+offset,SIZE/2),
									QPointF(SIZE/2,SIZE/2-offset))
			if "corner" in info:
				pattern = [-0.5,-0.5,0.5,0.5]
				corner = info["corner"]
				qp.drawArc(SIZE*pattern[corner],SIZE*(pattern[(corner+1)%4]),SIZE,SIZE,90*16*corner,90*16*(corner+5))
		qp.end()

class CommitLine(QWidget):
	clicked = pyqtSignal(int)
	def __init__(self,cells,data,index,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.cells = cells
		self.data=data
		self.index = index
		self.selected=False
		hbox = QHBoxLayout()
		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.setSpacing(0)
		self.setLayout(hbox)
		self.spacer = QWidget()
		self.spacer.setFixedWidth(10)
		self.label = QLabel(data["name"])
		self.label.setFixedWidth(150)
		hbox.addWidget(self.spacer)
		hbox.addWidget(self.label)
		for i,cell_data in enumerate(cells):
			if len(list(filter(lambda x: x!=[],cells[i:])))!=0:
				hbox.addWidget(Cell(cell_data))
		hbox.addWidget(QWidget())
		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
		self.setFixedHeight(SIZE)

	def mousePressEvent(self,event):
		self.clicked.emit(self.index)
		self.setStyleSheet("background-color: #333344;")

	def unselect(self):
		self.setStyleSheet("")

class Tree(QScrollArea):
	def __init__(self,commits,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.COLORS = ['#00B7C3','#744DA9','#C30052','#FFB900','#00CC6A']
		self.commits= commits
		self.initUI()

	def unselect_all(self,i):
		for line in self.lines:
			line.unselect()

	def calculate_tree(self):
		branches = list(set([commit['branch']['id'] for commit in self.commits]))
		self.grid = [[[] for i in branches]for i in self.commits]
		collumns = [None]*len(branches)
		used_collumns = [0]*len(branches) # last row used in each collumn
		self.commit_positions = {}
		for i, commit in enumerate(self.commits):
			branch_id = commit["branch"]["id"]
			commits_left = self.commits[i+1:]

			if branch_id in collumns: # branch is already active
				collumn = collumns.index(branch_id)
				if self.is_branch_dead(branch_id,commits_left): # last commit of the branch
					self.add_cell_data(i,collumn,{"dirs":[0],"symbol":True,"color": self.COLORS[collumn%len(self.COLORS)]},commit)
				else:
					self.add_cell_data(i,collumn,{"dirs":[0,2],"symbol":True,"color": self.COLORS[collumn%len(self.COLORS)]},commit)

			else: # branch doesn't exist, needs to be created
				is_dead = self.is_branch_dead(branch_id,commits_left)
				if i==0: # root
					collumns[0] = branch_id
					self.add_cell_data(i,0,{"dirs":[0 if is_dead else 2],"symbol":True,"color": self.COLORS[0]},commit)
				else: # new branch
					parent_pos = self.commit_positions[commit["parent"]]
					l = list(filter(lambda x: x[1]==None and used_collumns[x[0]]<parent_pos[0] and x[0]>parent_pos[1],enumerate(collumns)))
					collumn = l[0][0]
					collumns[collumn] = branch_id
					self.add_cell_data(i,collumn,{"dirs":[0 if is_dead else 2],"symbol":True,"color": self.COLORS[collumn%len(self.COLORS)]},commit)
					my_pos = self.commit_positions[commit["id"]]
					self.connect(my_pos,parent_pos)

			if commit["mergedFrom"]:
				self.connect(self.commit_positions[commit["mergedFrom"]],self.commit_positions[commit["id"]])

			for j,collumn in enumerate(collumns): # progress all active branches
				if collumn != branch_id and collumn!=None:
					self.add_cell_data(i,j,{"dirs":[0,2],"color": self.COLORS[j%len(self.COLORS)]})

			
			for j,branch in enumerate(collumns): # remove all dead branches
				if branch:
					if self.is_branch_dead(branch,commits_left):
						collumns[j]=None
						used_collumns[j]=i
		return self.grid

	def connect(self,start,end): # go straight from start, turn once at same height as end, color is start color
		d_y = end[0]-start[0]
		d_x = end[1]-start[1]
		dir_y = d_y//abs(d_y)
		dir_x = d_x//abs(d_x)

		CORNERS = {
		(1,1): 3,
		(1,-1): 2, 
		(-1,-1): 1,
		(-1,1): 0}
		color = self.COLORS[start[1]%len(self.COLORS)]
		self.add_cell_data(start[0],start[1],{"dirs":[0 if d_y<0 else 2],"color": color }) # start
		self.add_cell_data(end[0],end[1],{"dirs":[1 if d_x<0 else 3],"color": color}) # end
		self.add_cell_data(end[0],start[1],{"dirs":[],"corner":CORNERS[(dir_x,dir_y)],"color": color}) # corner

		for y in range(start[0],end[0],dir_y): # vertical
			self.add_cell_data(y,start[1],{"dirs":[0,2],"color": color})
		for x in range(start[1]+dir_x,end[1],dir_x): # vertical
			self.add_cell_data(end[0],x,{"dirs":[1,3],"color": color})


	def add_cell_data(self,x,y,info,commit=None):
		if "symbol" in info and info["symbol"]==True:
			info["symbol"] = "dot" if commit["mergedFrom"]==None else "merge"
		self.grid[x][y].append(info)
		if commit:
			self.commit_positions[commit["id"]] = (x,y)


	def is_branch_dead(self,branch,commits):
		return len(list(filter(lambda x: x["branch"]["id"]==branch or x["mergedFrom"]==branch,commits))) == 0

	def print_arr(self,arr):
		for line in arr:
			print(line)

	def initUI(self):
		self.widget = QWidget()
		self.vbox = QVBoxLayout()
		
		tree = self.calculate_tree()

		self.lines = []

		for i,commit in enumerate(tree):
			line = CommitLine(commit,self.commits[i],i)
			line.clicked.connect(self.unselect_all)
			self.lines.append(line)
			self.vbox.addWidget(line)

		self.vbox.setSpacing(0)
		self.vbox.setContentsMargins(0, 0, 0, 0)
		self.vbox.addWidget(QWidget()) # expanding spacer
		self.widget.setLayout(self.vbox) 
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidgetResizable(True)
		self.setWidget(self.widget)
		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

def main():
	app = QApplication(sys.argv)
	file = QFile("theme.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())
	win = QWidget()
	vbox = QVBoxLayout()

	connection = HTTPConnection("10.0.0.23:8080")
	connection.request("GET","/")
	response = connection.getresponse()
	data = response.read().decode()
	connection.close
	
	tree = Tree(json.loads(data))

	vbox.addWidget(tree)
	vbox.addWidget(QPushButton('Example'))

	win.setLayout(vbox)
	win.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
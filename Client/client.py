from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json

SIZE = 30

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
		for info in self.infos[::-1]:
			qp.setPen(QPen(QColor(info["color"]),2))
			for direction in info["dirs"]:
				pattern = [1,2,1,-2]
				qp.drawLine(SIZE/2,SIZE/2,(SIZE/2)*pattern[direction],(SIZE/2)*pattern[(direction-1)%4])
			if "symbol" in info:
				qp.setBrush(QColor(info["color"]))
				if info["symbol"]=="dot":
					qp.drawEllipse(QPointF(SIZE/2,SIZE/2),3,3)
				if info["symbol"]=="merge":
					qp.drawEllipse(QPointF(SIZE/2,SIZE/2),5,5)
			if "corner" in info:
				qp.drawArc(-SIZE/2,SIZE/2,SIZE,SIZE,0,90*16)

		qp.end()

class CommitLine(QWidget):
	clicked = pyqtSignal(int)
	
	def __init__(self,cells,data,index,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.cells = cells
		self.data=data
		self.index = index
		hbox = QHBoxLayout()
		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.setSpacing(0)
		self.setLayout(hbox)
		spacer = QWidget()
		spacer.setFixedWidth(10)
		self.label = QLabel(data["name"])
		self.label.setFixedWidth(150)
		hbox.addWidget(spacer)
		hbox.addWidget(self.label)
		for i,cell in enumerate(cells):
			if len(list(filter(lambda x: x!=[],cells[i:])))!=0:
				hbox.addWidget(Cell(cell))
		hbox.addWidget(QWidget())

		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
		self.setFixedHeight(SIZE)

	def mousePressEvent(self,event):
		self.clicked.emit(self.index)
		self.setStyleSheet("background-color: #ffffff;")


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
		grid = [[[] for i in branches]for i in self.commits]
		collumns = [None]*len(branches)
		dead = [0]*len(branches)
		commits = {}
		for i, commit in enumerate(self.commits):

			branch_id = commit["branch"]["id"]

			
			commits_left = self.commits[i+1:]
			if branch_id in collumns:
				collumn = collumns.index(branch_id)
				if self.is_branch_dead(branch_id,commits_left):
					self.add_cell_data(commits,grid,i,collumn,{"dirs":[0],"symbol":"dot","color": self.COLORS[collumn%len(self.COLORS)]},commit)
				else:
					self.add_cell_data(commits,grid,i,collumn,{"dirs":[0,2],"symbol":"dot","color": self.COLORS[collumn%len(self.COLORS)]},commit)
			else:
				is_dead = self.is_branch_dead(branch_id,commits_left)

				if i==0:
					collumns[0] = branch_id
					self.add_cell_data(commits,grid,i,0,{"dirs":[0 if is_dead else 2],"symbol":"dot","color": self.COLORS[0]})
				else:
					pos = commits[commit["parent"]]
					l = list(filter(lambda x: x[1]==None and dead[x[0]]<pos[0] and x[0]>pos[1],enumerate(collumns)))
					collumn = l[0][0]
					collumns[collumn] = branch_id
					self.add_cell_data(commits,grid,i,collumn,{"dirs":[0,0 if is_dead else 2],"symbol":"dot","color": self.COLORS[collumn%len(self.COLORS)]},commit)
					my_pos = commits[commit["id"]]
					self.add_cell_data(commits,grid,pos[0],pos[1],{"dirs":[1],"color": self.COLORS[collumn%len(self.COLORS)]})

					for row in range(my_pos[0]-1,pos[0],-1):
						self.add_cell_data(commits,grid,row,my_pos[1],{"dirs":[0,2],"color": self.COLORS[collumn%len(self.COLORS)]})

					for col in range(my_pos[1]-1,pos[1],-1):
						self.add_cell_data(commits,grid,pos[0],col,{"dirs":[1,3],"color": self.COLORS[collumn%len(self.COLORS)]})
					self.add_cell_data(commits,grid,pos[0],my_pos[1],{"dirs":[],"corner":1,"color": self.COLORS[collumn%len(self.COLORS)]})


			for j,collumn in enumerate(collumns):
				if collumn != branch_id and collumn!=None:
					self.add_cell_data(commits,grid,i,j,{"dirs":[0,2],"color": self.COLORS[j%len(self.COLORS)]})

			
			for j,branch in enumerate(collumns):
				if branch:
					if self.is_branch_dead(branch,commits_left):
						collumns[j]=None
						dead[j]=i
		return grid

	def add_cell_data(self,commits,grid,x,y,info,commit=None):
		grid[x][y].append(info)
		if commit:
			commits[commit["id"]] = (x,y)


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
	win = QWidget()
	vbox = QVBoxLayout()


	data = '''[{"id": 1, "name": "Init", "message": "Initial Commit", "parent": null, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 4, "name": "Bugfix", "message": "I fixed a bug", "parent": 1, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 5, "name": "Start Feature", "message": "start", "parent": 4, "branch": {"name": "Feature", "id": 4}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 6, "name": "Buf gix", "message": "bugfix", "parent": 4, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 7, "name": "Continue Feature", "message": "continue", "parent": 5, "branch": {"name": "Feature", "id": 4}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 8, "name": "Continuer Feature", "message": "continuing", "parent": 7, "branch": {"name": "Feature", "id": 4}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 9, "name": "Continuerer Feature", "message": "continuinging", "parent": 8, "branch": {"name": "Feature", "id": 4}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 10, "name": "Bug Add", "message": "bugadd", "parent": 6, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 11, "name": "Bug Add", "message": "bugadd", "parent": 6, "branch": {"name": "Feature2", "id": 5}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 12, "name": "Test 10", "message": "test", "parent": 10, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 13, "name": "Test 11", "message": "test", "parent": 11, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 14, "name": "Test 12", "message": "test", "parent": 12, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 15, "name": "Test 13", "message": "test", "parent": 13, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 16, "name": "Test 14", "message": "test", "parent": 14, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 17, "name": "Test 15", "message": "test", "parent": 15, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": 11}, {"id": 18, "name": "Test 16", "message": "test", "parent": 16, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 19, "name": "Test 17", "message": "test", "parent": 17, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 20, "name": "Test 18", "message": "test", "parent": 18, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}, {"id": 21, "name": "Test 19", "message": "test", "parent": 19, "branch": {"name": "Main", "id": 1}, "user": "Elon", "repo": "Tesla", "mergedFrom": null}]'''

	tree = Tree(json.loads(data))

	vbox.addWidget(tree)
	vbox.addWidget(QPushButton('Example'))

	win.setLayout(vbox)
	win.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
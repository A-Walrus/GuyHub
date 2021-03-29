from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import qtawesome as qta
from client import *

class Main():
	def __init__(self):
		self.app = get_app()
		self.ui = None
		self.client = Client()

	def set_ui(self,ui):
		if self.ui:
			self.ui.close()
			self.ui = ui
		else:
			self.ui = ui
			sys.exit(self.app.exec_())

	def update_ui(self):
		QCoreApplication.processEvents()

def get_app():
	app = QApplication(sys.argv)
	file = QFile("theme.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())
	return app

SIZE = 24


def getWindowTitle(page,item):
	return "%s - %s"%(page,item)

class BoxLayout(QWidget):
	def __init__(self,direction,*args,**kwargs):
		super().__init__(*args,**kwargs)
		if direction == "h":
			self.layout = QHBoxLayout()
		else:
			self.layout=QVBoxLayout()
		self.setLayout(self.layout)

	def addWidget(self,widget,*args,**kwargs):
		self.layout.addWidget(widget,*args,**kwargs)

class icon_input_line(QWidget):
	def getText(self):
		return self.line.text()

	def __init__(self,text,mode,icon_name,*args,**kwargs):
		super().__init__(*args,**kwargs)
		layout = QHBoxLayout()
		self.setLayout(layout)
		self.line = QLineEdit()
		self.line.setPlaceholderText(text)
		self.line.setEchoMode(mode)
		icon = qta.IconWidget()
		icon.setIcon(qta.icon(icon_name,color='white'))
		layout.addWidget(icon)
		layout.addWidget(self.line)

class Header(QLabel):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)

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

	def unselect(self):
		self.setStyleSheet("")

class Tree(QScrollArea):
	selected = pyqtSignal(dict,str)
	def __init__(self,commits,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.COLORS = ['#00B7C3','#744DA9','#C30052','#FFB900','#00CC6A']
		self.commits= commits
		self.initUI()

	def select_line(self,i):
		self.selected_id = i
		for j,line in enumerate(self.lines):
			if j!=i:
				line.unselect()
			else:
				line.setStyleSheet("background-color: #333344;")
				self.ensureWidgetVisible(line)
		self.selected.emit(self.commits[i],self.branch_colors[self.commits[i]["branch"]["id"]])

	def calculate_tree(self):
		branches = list(set([commit['branch']['id'] for commit in self.commits]))
		self.branch_colors={}
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
					self.add_cell_data(i,0,{"dirs":[] if is_dead else [2],"symbol":True,"color": self.COLORS[0]},commit)
					self.branch_colors[branch_id]= self.COLORS[0]
				else: # new branch
					parent_pos = self.commit_positions[commit["parent"]]
					l = list(filter(lambda x: x[1]==None and used_collumns[x[0]]<parent_pos[0] and x[0]>parent_pos[1],enumerate(collumns)))
					collumn = l[0][0]
					collumns[collumn] = branch_id
					self.add_cell_data(i,collumn,{"dirs":[0 if is_dead else 2],"symbol":True,"color": self.COLORS[collumn%len(self.COLORS)]},commit)
					my_pos = self.commit_positions[commit["id"]]
					self.connect(my_pos,parent_pos)
					self.branch_colors[branch_id]= self.COLORS[collumn%len(self.COLORS)]

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

		CORNERS = {(1,1): 3, (1,-1): 2, (-1,-1): 1,(-1,1): 0}
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

	def keyPressEvent(self, event):
		if self.hasFocus():
			if event.key() == Qt.Key_Up:
				self.select_line(max(self.selected_id-1,0))
			if event.key() == Qt.Key_Down:
				self.select_line(min(self.selected_id+1,len(self.commits)-1))
			

	def initUI(self):
		self.vbox = BoxLayout("v")
		
		tree = self.calculate_tree()

		self.lines = []

		for i,commit in enumerate(tree):
			line = CommitLine(commit,self.commits[i],i)
			line.clicked.connect(self.select_line)
			self.lines.append(line)
			self.vbox.addWidget(line)

		self.vbox.layout.setSpacing(0)
		self.vbox.setContentsMargins(0, 0, 0, 0)
		self.vbox.addWidget(QWidget()) # expanding spacer
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setWidgetResizable(True)
		self.setWidget(self.vbox)
		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

class RepoView(QWidget):
	def update_info(self,info,color):
		self.message.setText(info["message"])
		self.user.setText(info["user"])
		self.branch.setText(info["branch"]["name"])
		self.branch.setStyleSheet("color: %s"%color)
		self.name.setText(info["name"])


	def __init__(self,data,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.data = data

		self.setWindowTitle(getWindowTitle("Repo",self.data["repo"]["name"]))
		self.show()
		
		main_vbox = QVBoxLayout()

		hbox = BoxLayout("h")
		hbox.layout.setContentsMargins(0,0,0,0)

		self.tree = Tree(self.data["commits"])
		self.tree.selected.connect(self.update_info)


		
		info = BoxLayout("v")
		info.layout.setContentsMargins(0,0,0,0)

		self.message= QTextBrowser()
		self.message.setText("Commit Message")

		self.user= QLabel("User")
		self.branch = Header("Branch")
		self.name = Header("Commit")

		info.addWidget(self.name)
		info.addWidget(self.branch)
		info.addWidget(self.user)
		info.addWidget(self.message)


		splitter = QSplitter(Qt.Horizontal)

		splitter.addWidget(self.tree)
		splitter.addWidget(info)
		hbox.addWidget(splitter)

		header = Header(self.data["repo"]["name"])
		header.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
		main_vbox.addWidget(header)
		main_vbox.addWidget(hbox)

		self.setLayout(main_vbox)

		self.tree.select_line(len(self.data["commits"])-1)

class Login(QWidget):
	def set_label(self,textt,error=False):
		self.label.setText(textt)
		self.label.setStyleSheet("color: %s"%"#FFB900" if error else "white")

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.setWindowTitle("Login")
		self.show()

		window = BoxLayout("v")
		window.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

		self.label = Header("Hello User!")
		self.label.setAlignment(Qt.AlignCenter)
		window.addWidget(self.label)
		
		self.username = icon_input_line("username",QLineEdit.EchoMode.Normal,"fa5s.user")
		window.addWidget(self.username)

		self.password = icon_input_line("password",QLineEdit.EchoMode.Password,"fa5s.lock")
		window.addWidget(self.password)

		self.username.line.setText("Elon") # for testing
		self.password.line.setText("$TSLA") # for testing

		self.button = QPushButton("Login")
		self.button.clicked.connect(self.on_press)
		window.addWidget(self.button)

		grid = QGridLayout()
		grid.addWidget(window,1,1)
		self.setLayout(grid)

	def keyPressEvent(self, event):
		if self.password.line.hasFocus() or self.button.hasFocus() or self.username.line.hasFocus():
			if event.key() == Qt. Key_Return: 
				self.on_press()

	def on_press(self):
		username,password = self.username.getText(), self.password.getText()
		if username == "" or password =="":
			self.set_label("Username and password cannot be empty!",True)
		else:
			main.client.set_auth((username,password))
			self.set_label("Logging you in!")
			main.update_ui()
			r = main.client.get("profile")
			if r.status_code==200:
				main.set_ui(Profile(r.json()))
			else:
				self.set_label("Username or Password incorrect!",True)

class Profile(QWidget):
	def repo_selected(self):
		repo = self.repos.selectedIndexes()[0]
		id = self.branches[repo.data()]
		r = main.client.get(["repos",id])
		
		if r.status_code == 200:
			self.repo = r.json()
			self.branches_list.clear()
			for branch in r.json()["branches"]:
				self.branches_list.addItem("%s - %s"%(branch["name"],branch["owner"]))
		else:
			print(r)


	def on_press(self):
		if self.repo:
			main.set_ui(RepoView(self.repo))

	def __init__(self,data,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.data = data
		self.repo = None
		self.setWindowTitle(getWindowTitle("Profile",self.data["user"]["name"]))
		self.show()


		self.branches ={}
		for repo in self.data["repos"]:
			self.branches[repo["name"]] = repo["id"]

		info = BoxLayout("h")

		self.repos = QListWidget()
		self.repos.setSelectionMode(QAbstractItemView.SingleSelection)
		self.repos.itemSelectionChanged.connect(self.repo_selected)
		for repo in self.data["repos"]:
			self.repos.addItem(repo["name"])
		
		repo_view = BoxLayout("v")
		repo_view.addWidget(Header("Repos"))
		repo_view.addWidget(self.repos)

		open_button = QPushButton("Open Repo")
		repo_view.addWidget(open_button)
		open_button.clicked.connect(self.on_press)


		self.branches_list = QListWidget()
		self.branches_list.setSelectionMode(QAbstractItemView.NoSelection)
		branch_view = BoxLayout("v")
		branch_view.addWidget(Header("Branches"))
		branch_view.addWidget(self.branches_list)

		info.addWidget(repo_view)
		info.addWidget(branch_view)

		layout = QVBoxLayout()
		self.setLayout(layout)
		layout.addWidget(Header("%s's Profile"%self.data["user"]["name"]))
		layout.addWidget(info)

main = Main()
main.set_ui(Login())
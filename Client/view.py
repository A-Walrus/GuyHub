from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

import qtawesome as qta
from App.control import *
import re


SIZE = 24


class Screen(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.setWindowIcon(QIcon('App/logo.png'))
		self.children=[]
		self.were_shown=[]

	def close(self):
		self.were_shown=[]
		super().close()
		for child in self.children:
			if child.isVisible():
				self.were_shown.append(child)
				child.close()

	def show(self):
		super().show()
		for child in self.were_shown:
			child.show()

class Main():
	def __init__(self):
		self.app = get_app()
		self.ui = None
		self.ui_history=[]

	def set_ui(self,ui,replace_history = False):
		if self.ui:
			self.ui_history.append(self.ui)
			if replace_history:
				self.ui_history.pop()
			self.ui.close()
			self.ui = ui
		else:
			self.ui = ui
			sys.exit(self.app.exec_())
		self.ui.show()


	def update_ui(self):
		QCoreApplication.processEvents()

def get_app():
	app = QApplication(sys.argv)
	file = QFile("App/theme.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())
	return app

def getWindowTitle(items):
	return " - ".join(items)

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

class ButtonRow(BoxLayout):
	def __init__(self,*args,**kwargs):
		super().__init__('h',*args,**kwargs)

	def add_button(self,text,function):
		button = QPushButton(text)
		button.clicked.connect(function)
		self.addWidget(button)

class icon_input_line(QWidget):
	def getText(self):
		return self.line.text()

	def __init__(self,text,icon_name,mode=QLineEdit.EchoMode.Normal,*args,**kwargs):
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

class Window(Screen):
	def __init__(self,data_func=None,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.data_func= data_func
		vbox = QVBoxLayout()
		button = QPushButton(qta.icon('mdi.keyboard-backspace',color='white'),"Back")
		button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		button.clicked.connect(self.back)
		self.w= QWidget()
		vbox.addWidget(self.w)
		vbox.addWidget(button)
		self.setLayout(vbox)

	def back(self):
		if len(main.ui_history)>0:
			ui = main.ui_history.pop()
			main.set_ui(ui)
			main.ui_history.pop() # pop self

	def reload(self):
		if self.data_func:
			data = self.data_func()
			main.set_ui(type(self)(data),True)

class Cell(QWidget):
	def __init__(self,infos,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.infos = infos
		self.setFixedSize(SIZE,SIZE)

	def drawBase(self,event): # draw the base class
		super().paintEvent(event)
		opt = QStyleOption()
		opt.initFrom(self)
		p = QPainter(self)
		s = self.style()
		s.drawPrimitive(QStyle.PE_Widget, opt, p, self) 

	def paintEvent(self, event): # called when Qt wants to paint this widget
		self.drawBase(event) 
		qp = QPainter() # create a qpainter
		qp.begin(self) # start painting on self
		qp.setRenderHint(QPainter.Antialiasing) # turn on anti aliasing 
		for info in self.infos[::-1]:
			qp.setPen(QPen(QColor(info["color"]),2)) # set pen to color and width
			for direction in set(info["dirs"]):
				pattern = [1,2,1,-2]
				qp.drawLine(SIZE/2,SIZE/2,(SIZE/2)*pattern[direction],(SIZE/2)*pattern[(direction-1)%4]) # draw a line between x1,y1, x2,y2
			if "symbol" in info:
				qp.setBrush(QColor(info["color"]))
				if info["symbol"]=="dot":
					qp.drawEllipse(QPointF(SIZE/2,SIZE/2),3,3) # draw a circle at a point
				if info["symbol"]=="merge":
					offset = 6
					qp.drawPolygon(	QPointF(SIZE/2-offset,SIZE/2),
									QPointF(SIZE/2,SIZE/2+offset),
									QPointF(SIZE/2+offset,SIZE/2),
									QPointF(SIZE/2,SIZE/2-offset)) # draw a rotated square
			if "corner" in info:
				pattern = [-0.5,-0.5,0.5,0.5]
				corner = info["corner"]
				qp.drawArc(SIZE*pattern[corner],SIZE*(pattern[(corner+1)%4]),SIZE,SIZE,90*16*corner,90*16*(corner+5)) # draw a rounded corner
		qp.end() # end the painter

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
		self.label.setFixedWidth(250)
		hbox.addWidget(self.spacer)
		hbox.addWidget(self.label)

		for i,cell_data in enumerate(cells):
			if len(list(filter(lambda x: x!=[],cells[i:])))!=0:
				hbox.addWidget(Cell(cell_data))

		hbox.addWidget(QWidget())
		self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
		self.setFixedHeight(SIZE)


	def mousePressEvent(self,event):
		if event.button() == Qt.LeftButton:
			self.clicked.emit(self.index)
		elif event.button() == Qt.RightButton:
			main.ui.merge(self.data)
	
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
				line.setStyleSheet("background-color: #333344")
				self.ensureWidgetVisible(line)
		self.selected.emit(self.commits[i],self.branch_colors[self.commits[i]["branch"]["id"]])

	def calculate_tree(self):
		branches = list(set([commit['branch']['id'] for commit in self.commits]))
		self.branch_colors={}
		self.grid = [[[] for i in branches]for i in self.commits]
		collumns = [None]*len(branches)
		used_collumns = [-1]*len(branches) # last row used in each collumn
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
					l = list(filter(lambda x: x[1]==None and used_collumns[x[0]]<parent_pos[0] and x[0]>parent_pos[1]  ,enumerate(collumns)))
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

		for y in range(start[0]+dir_y,end[0],dir_y): # vertical
			self.add_cell_data(y,start[1],{"dirs":[0,2],"color": color})
		for x in range(start[1]+dir_x,end[1],dir_x): # horizontal
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

class Request(BoxLayout):
	def respond(self,val):
		control.respond(self.id,val)
		main.ui.reload()

	def view(self,id,text):
		c = CommitFiles(id,text)
		c.show()
		self.commit_files.append(c)

	def __init__(self,by,to,name,id,parent,*args,**kwargs):
		super().__init__('h',*args,**kwargs)
		self.commit_files=[]
		self.id = id
		self.parent= parent
		text = f'Request: <b>{name}</b> by <b>{by}</b> to <b>{to}</b>'

		if control.session.auth[0] == to: # if user is the owner of the branch, and can accept or reject requests
			accept = QToolButton()
			accept.setIcon(qta.icon('fa5s.check-square',color="#27ae60"))
			accept.clicked.connect(lambda : self.respond(True))
			self.addWidget(accept)

			reject = QToolButton()
			reject.setIcon(qta.icon('fa5s.window-close',color="#e74c3c"))
			reject.clicked.connect(lambda : self.respond(False))
			self.addWidget(reject)

		self.addWidget(QLabel(text))
		b = QPushButton("View")
		b.clicked.connect(lambda : self.view(self.id,"Request"))
		self.addWidget(b)

		b = QPushButton("View Parent")
		b.clicked.connect(lambda : self.view(self.parent,"Request Parent"))
		self.addWidget(b)

class Requests(QScrollArea):
	def __init__(self,requests,users_d,*args,**kwargs):
		super().__init__(*args,**kwargs)
		users = {}
		for user in users_d:
			users[user["id"]] = user["name"]
		print(users)

		vbox =  BoxLayout("v")
		self.setMinimumWidth(300)
		for request in requests:
			print(request)
			print(request)
			vbox.addWidget(Request(users[request["from"]],users[request["to"]],request["name"],request["id"],request["parent"]))

		self.setWidget(vbox)

class RepoView(Window):
	def update_info(self,info,color):
		self.selected = info
		self.message.setText(info["message"])
		self.user.setText(info["user"])
		self.branch.setText(info["branch"]["name"])
		self.branch.setStyleSheet("color: %s"%color)
		self.name.setText(info["name"])

	def fetch(self):
		control.pull_commit(self.selected["id"],self.selected["repo"]["id"],True)

	def add_user(self):
		self.children.append(AddUser(self.data))

	def merge(self,data):
		self.children.append(Merge(self.selected,data))

	def set_path(self):
		file=''
		while file=='':
			file = str(QFileDialog.getExistingDirectory(self, "Select Working Directory For %s"%self.data["repo"]["name"]))
		control.set_location(self.data["repo"]["id"],file)
		self.setWindowTitle(getWindowTitle(["Repo",self.data["repo"]["name"],control.get_repo_path(self.data["repo"]["id"])]))

	def commit(self):
		self.children.append(Commit(self.selected))


	def fork(self):
		self.children.append(Fork(self.selected))

	def download(self):
		control.pull_commit(self.selected["id"],self.selected["repo"]["id"],False)

	def open(self):
		files = CommitFiles(self.selected["id"],self.selected["name"],repo_id = self.selected["repo"]["id"])
		self.children.append(files)
		files.show()

	def __init__(self,data,*args,**kwargs):
		super().__init__(lambda : control.get_repo(self.data["repo"]["id"]).json(),*args,**kwargs)
		self.data = data
		path = control.get_repo_path(self.data["repo"]["id"])
		if path:
			self.setWindowTitle(getWindowTitle(["Repo",self.data["repo"]["name"],path]))
		else:
			self.set_path()


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

		self.requests = Requests(data["requests"],data["users"])
		


		splitter.addWidget(self.tree)
		splitter.addWidget(info)
		hbox.addWidget(splitter)
		hbox.addWidget(self.requests)

		header = Header(self.data["repo"]["name"])

		add_user = QPushButton("Add User")
		add_user.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		add_user.clicked.connect(self.add_user)

		set_path = QPushButton("Set Repo Path")
		set_path.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		set_path.clicked.connect(self.set_path)

		reload_button = QPushButton("Reload")
		reload_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		reload_button.clicked.connect(self.reload)


		top = BoxLayout("h")
		top.addWidget(header)
		row = ButtonRow()
		row.add_button("Reload",self.reload)
		row.add_button("Add user",self.add_user)
		row.add_button("Set Repo Path",self.set_path)
		top.addWidget(row)
		top.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))


		main_vbox.addWidget(top)
		main_vbox.addWidget(hbox)
		
		bottom = ButtonRow()
		bottom.add_button("Fetch",self.fetch)
		bottom.add_button("Download",self.download)
		bottom.add_button("Commit",self.commit)
		bottom.add_button("Fork",self.fork)
		bottom.add_button("Open",self.open)

		bottom.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

		main_vbox.addWidget(bottom)

		self.w.setLayout(main_vbox)

		self.show() # in order for select_line to work
		self.tree.select_line(len(self.data["commits"])-1)

class Profile(Window):
	def new_repo(self):
		self.children.append(NewRepo())

	def repo_selected(self):
		repo = self.repos.selectedIndexes()[0]
		id = self.repo_n_id[repo.data()]
		r = control.get_repo(id)
		
		if r.status_code == 200:
			self.repo = r.json()
			self.users_list.clear()
			for user in r.json()["users"]:
				self.users_list.addItem(user["name"])
		else:
			print(r)

	def on_press(self):
		if self.repo:
			main.set_ui(RepoView(self.repo))

	def __init__(self,data,*args,**kwargs):
		super().__init__(lambda :  control.get_profile().json(),*args,**kwargs)
		self.data = data
		self.repo = None
		self.setWindowTitle(getWindowTitle(["Profile",self.data["user"]["name"]]))
		self.repo_n_id ={}
		for repo in self.data["repos"]:
			self.repo_n_id[repo["name"]] = repo["id"]


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
		open_button.clicked.connect(self.on_press)
		repo_view.addWidget(open_button)

		new_repo = QPushButton("Create New Repo")
		new_repo.clicked.connect(self.new_repo)
		repo_view.addWidget(new_repo)

		self.users_list = QListWidget()
		self.users_list.setSelectionMode(QAbstractItemView.NoSelection)
		user_view = BoxLayout("v")
		user_view.addWidget(Header("Users"))
		user_view.addWidget(self.users_list)

		info.addWidget(repo_view)
		info.addWidget(user_view)

		layout = QVBoxLayout()
		self.w.setLayout(layout)
		layout.addWidget(Header("%s's Profile"%self.data["user"]["name"]))
		layout.addWidget(info)
		self.show()

class PopUp(BoxLayout,Screen):
	def __init__(self,header,fixed=True,*args,**kwargs):
		super().__init__("v",*args,**kwargs)
		self.addWidget(Header(header))
		self.setWindowTitle(header)
		self.initUI()
		self.show()
		if(fixed):
			self.setFixedSize(self.size())

class AddUser(PopUp):
	def pressed(self):
		if self.combo.currentText() in self.users_dict:
			repo = self.data["repo"]["id"]
			user = self.users_dict[self.combo.currentText()]
			control.add_user_to_repo(repo,user)
			self.close()
			main.ui.reload()

	def __init__(self,data,*args,**kwargs):
		self.data = data
		super().__init__("Add User to %s"%self.data["repo"]["name"],*args,**kwargs)
		

	def initUI(self):

		self.combo = QComboBox()
		users = [user["name"] for user in self.data["users"]]
		r = control.get_users()
		self.users_dict = {user["name"]:user["id"] for user in r["users"]}
		self.combo.addItems([user["name"] for user in r["users"] if not user["name"] in users])
		self.addWidget(self.combo)
		button = QPushButton("Add User")
		button.clicked.connect(self.pressed)
		self.addWidget(button)

class Commit(PopUp):
	def pressed(self):
		control.commit(self.data["id"],self.data["repo"]["id"],self.data["branch"]["id"],self.name.getText(),self.message.getText())
		main.ui.reload()
		self.close()

	def __init__(self,data,*args,**kwargs):
		self.data = data
		super().__init__("Commit",*args,**kwargs)
		

	def initUI(self):
		self.name = icon_input_line("Name","fa5s.angle-right")
		self.message = icon_input_line("message","fa5s.angle-double-right")
		self.addWidget(self.name)
		self.addWidget(self.message)

		button = QPushButton("Commit")
		button.clicked.connect(self.pressed)
		self.addWidget(button)
		
class Fork(PopUp):
	def pressed(self):
		name = self.line.getText()
		if name!="":
			control.fork(self.data["id"],name)
			main.ui.reload()
			self.close()

	def __init__(self,data,*args,**kwargs):
		self.data=data
		super().__init__("Fork",*args,**kwargs)

	def initUI(self):
		self.line = icon_input_line("Branch Name","mdi.directions-fork")
		self.button = QPushButton("Fork")
		self.button.clicked.connect(self.pressed)

		self.addWidget(self.line)
		self.addWidget(self.button)

class NewRepo(PopUp):
	def pressed(self):
		name = self.line.getText()
		print(name)
		control.create_repo(name)
		self.close()
		main.ui.reload()

	def __init__(self,*args,**kwargs):
		super().__init__("Create Repo",*args,**kwargs)

	def initUI(self):
		self.line = icon_input_line("Repo Name","mdi.source-repository")
		self.button = QPushButton("Create")
		self.button.clicked.connect(self.pressed)

		self.addWidget(self.line)
		self.addWidget(self.button)

class FileView(BoxLayout,Screen):
	def __init__(self,path,*args,**kwargs):
		super().__init__("v",*args,**kwargs)
		self.header = Header(path)
		self.addWidget(self.header)
		self.text = QTextBrowser()
		self.addWidget(self.text)
		self.update(path)


	def update(self,path):
		self.path = path
		self.header.setText(path)
		self.text.setText(FileView.read(path))

	def read(path):
		with open(path,"r")as f:
			try:
				return(f.read())
			except UnicodeDecodeError:
				return "File is not a text file!"

class CommitFiles(BoxLayout,Screen):
	def clear(self):
		self.tree.selectionModel().clearSelection()

	def showF(self):
		for path in self.get_selected():
			if "." in path:
				view = FileView(path)
				view.show()
				self.children.append(view)

	def grab(self):
		for path in self.get_selected():
			if "." in path:
				p = control.relative_path(path)
				with open(os.path.join(control.get_repo_path(self.repo_id),p),"wb") as w:
					with open(path,"rb") as r:
						w.write(r.read())

	def history(self):
		for path in self.get_selected():
			if "." in path:
				self.children.append(History(control.relative_path(path),self.repo_id,self.id))


	def __init__(self,id,header=None,multi=False,repo_id=None,*args,**kwargs):
		super().__init__("v",*args,**kwargs)

		self.id=id

		control.ensure_in_pulls(id)

		if header:
			self.addWidget(Header(header))

		self.tree = QTreeView()

		if multi==True:
			self.tree.setSelectionMode(QAbstractItemView.MultiSelection)
		path = control.get_pull_path(id)


		self.model = QFileSystemModel()
		self.model.setRootPath(QDir.rootPath())
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(path))

		self.addWidget(self.tree)
		buttons = ButtonRow()
		buttons.add_button("Select All",self.tree.selectAll)
		buttons.add_button("Deselect All",self.clear)
		buttons.add_button("Show File",self.showF)
		buttons.add_button("History",self.history)
		if repo_id:
			self.repo_id=repo_id
			buttons.add_button("Grab to Working",self.grab)
		self.addWidget(buttons)


	def get_selected(self):
		s = self.tree.selectedIndexes()
		indexes = [s[i] for i in range(0,len(s),4)]
		paths = list(map(self.model.filePath,indexes))
		return paths

class Merge(PopUp):
	def __init__(self,merge_to,merge_from,*args,**kwargs):
		self.merge_to=merge_to
		self.merge_from=merge_from
		super().__init__("Merge Commits",False,*args,**kwargs)
		
	def merge(self):
		paths = self.to_widget.get_selected()
		paths+=self.from_widget.get_selected()
		try:
			control.merge(paths,self.merge_to,self.merge_from)
			self.close()
			main.ui.reload()
		except (Duplicate, NoneSelected):
			print("oh no")
		


	def initUI(self):

		commits = BoxLayout('h')
		self.to_widget = CommitFiles(self.merge_to["id"],"To",True)
		self.from_widget = CommitFiles(self.merge_from["id"],"From",True)
		commits.addWidget(self.to_widget)
		commits.addWidget(self.from_widget)

		self.addWidget(commits)

		button = QPushButton("Merge")
		button.clicked.connect(self.merge)
		self.addWidget(button)

class CenterVboxWindow(Screen):
	def onClick(self):
		main.set_ui(self.buttonPage())

	def __init__(self,buttonText,buttonPage,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.show()
		self.w = BoxLayout("v")
		self.w.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
		self.buttonPage= buttonPage

		grid = QGridLayout()
		grid.addWidget(self.w,1,1)
		grid_w = QWidget()
		grid_w.setLayout(grid)
		corner = QPushButton(buttonText)
		corner.clicked.connect(self.onClick)
		corner.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

		layout = QVBoxLayout()
		layout.addWidget(corner)
		layout.addWidget(grid_w)
		self.setLayout(layout)

class Login(CenterVboxWindow,Screen):
	def set_label(self,text,error=False):
		self.label.setText(text)
		self.label.setStyleSheet("color: %s"%"#FFB900" if error else "white")

	def __init__(self,*args,**kwargs):
		super().__init__("Register",Register,*args,**kwargs)
		self.setWindowTitle("Login")

		self.label = Header("Login")
		self.label.setAlignment(Qt.AlignCenter)
		self.w.addWidget(self.label)
		
		self.username = icon_input_line("username","fa5s.user")
		self.w.addWidget(self.username)

		self.password = icon_input_line("password","fa5s.lock",QLineEdit.EchoMode.Password)
		self.w.addWidget(self.password)

		self.username.line.setText("Guy") # for testing
		self.password.line.setText("pass_guy") # for testing

		self.button = QPushButton("Login")
		self.button.clicked.connect(self.on_press)
		self.w.addWidget(self.button)

	def keyPressEvent(self, event):
		if self.password.line.hasFocus() or self.button.hasFocus() or self.username.line.hasFocus():
			if event.key() == Qt. Key_Return: 
				self.on_press()

	def on_press(self):
		username,password = self.username.getText(), self.password.getText()
		if username == "" or password =="":
			self.set_label("Username and password cannot be empty!",True)
		else:
			control.set_auth((username,password))
			self.set_label("Logging you in!")
			main.update_ui()
			r = control.get_profile()
			if r.status_code==200:
				main.set_ui(Profile(r.json()))
			else:
				self.set_label("Username or Password incorrect!",True)

class Register(CenterVboxWindow,Screen):
	def set_label(self,text,error=False):
		self.label.setText(text)
		self.label.setStyleSheet("color: %s"%"#FFB900" if error else "white")

	def __init__(self,*args,**kwargs):
		super().__init__("Login",Login,*args,**kwargs)
		self.setWindowTitle("Register")

		self.label = Header("Register")
		self.label.setAlignment(Qt.AlignCenter)
		self.w.addWidget(self.label)
		
		self.username = icon_input_line("username","fa5s.user")
		self.w.addWidget(self.username)

		self.password = icon_input_line("password","fa5s.lock",QLineEdit.EchoMode.Password)
		self.w.addWidget(self.password)

		self.password2 = icon_input_line("confirm password","fa5s.lock",QLineEdit.EchoMode.Password)
		self.w.addWidget(self.password2)

		self.button = QPushButton("Register")
		self.button.clicked.connect(self.on_press)
		self.w.addWidget(self.button)

	def keyPressEvent(self, event):
		if self.password.line.hasFocus() or self.button.hasFocus() or self.username.line.hasFocus() or self.password2.line.hasFocus():
			if event.key() == Qt. Key_Return: 
				self.on_press()

	def on_press(self):
		username,password,password2 = self.username.getText(), self.password.getText(), self.password2.getText()
		if username == "" or password =="" or password2=="":
			self.set_label("Username and password cannot be empty!",True)
		elif password2!=password:
			self.set_label("Passwords don't match!",True)
		else:
			self.set_label("Signing you up!")
			main.update_ui()
			r = control.post('register',{"User":username,"Pass":password})
			if r.status_code==200:
				control.set_auth((username,password))
				r = control.get_profile()
				main.set_ui(Profile(r.json()))
			else:
				self.set_label("Username taken!",True)

class History(BoxLayout,Screen):

	def trace(self,id):
		if id==-1:
			return []
		else:
			return [id] + self.trace(self.dict[id]["parent"])

	def gen_list(self):
		history = []
		for commit in self.history:
			path = control.ensure_in_pulls(commit)
			if os.path.exists(os.path.join(path,self.file)):
				history.append(commit)
			else:
				break
		filtered=[history[-1]]
		for item in range(len(history)-1):
			if FileView.read(os.path.join(control.get_pull_path(history[item]),self.file))!=FileView.read(os.path.join(control.get_pull_path(history[item+1]),self.file)):
				filtered.append(history[item])
		return filtered

	def create_item(self,id):
		item = QListWidgetItem(self.dict[id]["name"],self.commit_list)
		item.id = id
		return item

	def selected(self,item,prev):
		path = os.path.join(control.get_pull_path(item.id),self.file)
		self.fileView.update(path)

	def __init__(self,file,repo,commit,*args,**kwargs):
		super().__init__("h",*args,**kwargs)

		self.setMinimumSize(500,300)

		self.file=file

		self.show()
		self.commit_list = QListWidget()
		self.addWidget(self.commit_list)
		self.fileView=FileView(os.path.join(control.get_pull_path(commit),file))
		self.addWidget(self.fileView)

		commits = main.ui.data["commits"]
		self.dict = {}
		for commit in commits:
			self.dict[commit["id"]]=commit
		self.history = self.trace(commit["id"])

		for commit in self.gen_list():
			self.create_item(commit) 
		
		self.commit_list.currentItemChanged.connect(self.selected)


control = Control()
main = Main()
main.set_ui(Login())
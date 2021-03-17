import sqlite3 as lite
from PyQt5 import QtCore, QtGui, QtWidgets

def GetText(item):
	return "%s - %s : %s"%(item[2],item[4],item[1])


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(800, 600)
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
		self.gridLayout.setObjectName("gridLayout")
		self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
		self.treeWidget.setObjectName("treeWidget")

		conn = lite.connect(r"D:\Users\Guy\School\cyber\GuyHub\Server\GuyHub.db")
		print ("Opened database successfully")
		cursor = conn.cursor()
		cursor.execute('''	SELECT Commits.ID,Users.Name,Commits.Name,Commits.Parent,Branches.Name, Repos.Name 
							FROM Users JOIN Commits ON Users.ID = Commits.User 
							JOIN Branches ON Commits.Branch = Branches.ID 
							Join Repos On Repos.ID = Branches.Repo 
							Where Repos.ID = 1''')

		rows = cursor.fetchall()
		rows = [list(i) for i in rows]
		print(rows)
		tree = {}
		for i in rows:
			if i[0] == i[3]:
				item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
				item_0.setText(0,GetText(i))
				rows.remove(i)
				tree[i[0]]= item_0
		for i in rows:
			new_item = QtWidgets.QTreeWidgetItem(tree[i[3]])
			new_item.setText(0,GetText(i))
			tree[i[0]]=new_item


		self.gridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)

		QtCore.QMetaObject.connectSlotsByName(MainWindow)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
from http.client import HTTPSConnection
import ssl

from ui import *





def main():
	app = QApplication(sys.argv)
	file = QFile("theme.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())


	connection = HTTPSConnection("localhost:8080 ",context=ssl._create_unverified_context())
	connection.request("GET","/repos/1")
	response = connection.getresponse()
	data = response.read().decode()
	connection.close()
	
	
	win = RepoView(json.loads(data))
	
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
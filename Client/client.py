from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
from http.client import HTTPSConnection
import ssl

from ui import *


class http_handler():
	def __init__(self):
		self.connection = HTTPSConnection("localhost:8080 ",context=ssl._create_unverified_context())
		self.token = ""
		

	def login(self,user_name,password):
		self.connection.request("POST","/login",json.dumps({"name":user_name,"pass":password}),{'Content-type': 'application/json'})
		response = self.connection.getresponse()
		data = response.read().decode()
		data = self.error_handle(data)
		if data:
			self.token = data["token"]

	def request(self,url):
		self.connection.request("GET",url,None,{'token':self.token})
		response = self.connection.getresponse()
		data = response.read().decode()
		return self.error_handle(data)

		
	def error_handle(self,data):
		data = json.loads(data)
		if "error" in data:
			ErrorMessage(data["error"])
		else:
			return data

	def close(self):
		self.connection.close()


def main():
	app = QApplication(sys.argv)
	file = QFile("theme.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())

	http = http_handler()

	http.login("Elon","$TSLA")

	data = http.request("/repos/1")

	http.close()
	
	win = RepoView(data)
	
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
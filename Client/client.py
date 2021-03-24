from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
from http.client import HTTPSConnection
import ssl

from ui import *

class Error():
	def __init__(self,msg):
		self.msg = msg


class http_handler():
	def __init__(self):
		self.connection = HTTPSConnection("localhost:8080 ",context=ssl._create_unverified_context())
		self.token = ""
		

	def login(self,user_name,password):
		self.connection.request("POST","/login",json.dumps({"name":user_name,"pass":password}),{'Content-type': 'application/json'})
		response = self.connection.getresponse()
		data = response.read().decode()
		data = self.error_handle(data)
		if not isinstance(data, Error):
			self.token = data["token"]
			return None
		else:
			return data

	def request(self,url):
		self.connection.request("GET",url,None,{'token':self.token})
		response = self.connection.getresponse()
		data = response.read().decode()
		return self.error_handle(data)

		
	def error_handle(self,data):
		data = json.loads(data)
		if "error" in data:
			return Error(data["error"])
		else:
			return data

	def close(self):
		self.connection.close()


def submit(username,password):
	if username == "" or password =="":
		login.set_label("Username and password cannot be empty!")
	else:
		login.set_label("Logging you in!")
		QCoreApplication.processEvents()
		res = http.login(username,password)
		if isinstance(res,Error):
			login.set_label(res.msg,"#C30052")
		else:
			login.set_label("Success!")
			QCoreApplication.processEvents()
			data = http.request("/repos/1")
			if not isinstance(data, Error):
				login.close()
				print("HI")
				global repo
				repo = RepoView(data)
			else:
				login.set_label(data.msg)


def main():
	app = get_app()
	global http
	http = http_handler()
	global login
	login = Login()
	login.submit.connect(submit)


	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
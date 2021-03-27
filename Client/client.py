from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import requests
import ssl
from ui import *
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # supress ssl certificate warning, because I trust my own server

class Client():

	def get_url(self,path):
		return "https://%s:%s/%s"%('localhost',5000,path)

	def __init__(self):
		self.app = get_app()
		self.ui = Login()
		self.ui.submit.connect(self.submit)
		sys.exit(self.app.exec_())

	def get_session(self,auth):
		s = requests.Session()
		s.verify = False
		s.auth = (auth[0],auth[1])
		self.session = s

	def submit(self,username,password):
		if username == "" or password =="":
			self.ui.set_label("Username and password cannot be empty!",True)
		else:
			self.get_session((username,password))
			r = self.session.get(self.get_url("profile"))
			if r.status_code==200:
				self.ui.set_label("Success")
				print(r.json())
				self.ui.close()
				self.ui = Profile(r.json())
				# r = self.session.get(self.get_url("repos/1"))
				# self.ui.close()
				# self.ui = RepoView(r.json())
			else:
				self.ui.set_label("Username or Password incorrect!",True)


if __name__ == '__main__':
    client = Client()
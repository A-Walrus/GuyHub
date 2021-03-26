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

def get_session(auth):
	s = requests.Session()
	s.verify = False
	s.auth = (auth[0],auth[1])
	return s

def submit(username,password):
	if username == "" or password =="":
		login.set_label("Username and password cannot be empty!",True)
	else:
		s = get_session((username,password))
		r = s.get("https://localhost:5000/profile")
		if r.status_code==200:
			login.set_label("Success")
			r = s.get("https://localhost:5000/repos/1")
			global repo
			repo = RepoView(r.json())
		else:
			login.set_label("Username or Password incorrect!",True)


def main():
	app = get_app()
	global login
	login = Login()
	login.submit.connect(submit)
	sys.exit(app.exec_())

if __name__ == '__main__':
    main()
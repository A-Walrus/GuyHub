from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import requests
import ssl
from ui import *


def submit(username,password):
	if username == "" or password =="":
		login.set_label("Username and password cannot be empty!")
	else:
		for i in range(5):
				r = requests.get("https://localhost:8080/repos/%s"%i,verify=False,headers={'name' : 'Elon','pass':'$TSLA'})
				print(r.json())


def main():
	app = get_app()
# 	global http
# 	http = http_handler()
	global login
	login = Login()
	login.submit.connect(submit)
	sys.exit(app.exec_())

if __name__ == '__main__':
    main()
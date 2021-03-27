from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import requests
import ssl
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # supress ssl certificate warning, because I trust my own server

class Client():

	def get_url(self,path):
		return "https://%s:%s/%s"%('localhost',5000,path)

	def __init__(self):
		self.auth  = ("User","Pass")
		self.session = None


	def set_auth(self,auth):
		self.auth = auth
		self.get_session()

	def get_session(self):
		s = requests.Session()
		s.verify = False
		s.auth = self.auth
		self.session = s

	def get(self,path):
		if isinstance(path, str):
			url = self.get_url(path)
		else:
			url = self.get_url("/".join([str(item) for item in path]))
		return self.session.get(url)

if __name__ == '__main__':
    client = Client()
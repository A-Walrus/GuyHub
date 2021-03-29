import sys
import json
import requests
import ssl
from urllib3.exceptions import InsecureRequestWarning
import os
import shutil
import base64

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # supress ssl certificate warning, because I trust my own server

class Client():

	def get_url(self,path):
		if isinstance(path, str):
			path = path
		else:
			path = "/".join([str(item) for item in path])
		return "https://%s:%s/%s"%('localhost',5000,path)

	def __init__(self):
		self.auth  = ("User","Pass")
		self.get_session()


	def set_auth(self,auth):
		self.session.auth = auth

	def get_session(self):
		s = requests.Session()
		s.verify = False
		s.auth = self.auth
		self.session = s

	def get(self,path):
		return self.session.get(self.get_url(path))

	def post_file(self,path,file_path):
		return self.session.post(self.get_url(path),files = {'file': open(file_path, 'rb')})

def gen_commit(path):
	pass



if __name__ == '__main__':
	pass


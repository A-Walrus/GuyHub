import sys, json, requests, ssl
from urllib3.exceptions import InsecureRequestWarning
import os
from zipfile import ZipFile
from pathlib import Path
from winreg import *

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # supress ssl certificate warning, because I trust my own server

locations = "repo_locations.json"

def get_downloads_folder():
	with OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
		return QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]


class Client():

	def get_repo_path(self,id):
		if str(id) in self.locations:
			return self.locations[str(id)]
		else:
			return None


	def get_url(self,path):
		if isinstance(path, str):
			path = path
		else:
			path = "/".join([str(item) for item in path])
		return "https://%s:%s/%s"%('localhost',5000,path)

	def __init__(self):
		self.auth  = ("User","Pass")
		self.get_session()
		with open(locations) as file:
			self.locations = json.load(file)

	def set_auth(self,auth):
		self.session.auth = auth

	def get_session(self):
		s = requests.Session()
		s.verify = False
		s.auth = self.auth
		self.session = s

	def get(self,path):
		return self.session.get(self.get_url(path))

	def pull_commit(self,commit_id,repo_id,to_working):
		FILE = "pulls/%s.zip"%repo_id
		r = self.get(["commits",commit_id])
		open(FILE,'wb').write(r.content)
		with ZipFile(FILE, 'r') as zipObj:
			path = self.get_repo_path(repo_id) if to_working else "%s/commit"%get_downloads_folder()
			zipObj.extractall(path)

	def set_location(self,repo_id,path):
		self.locations[str(repo_id)]=path
		with open(locations, 'w') as outfile:
			json.dump(self.locations, outfile)




if __name__ == '__main__':
	pass


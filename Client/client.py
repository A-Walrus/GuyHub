import sys, json, requests, ssl
from urllib3.exceptions import InsecureRequestWarning
import os
from zipfile import ZipFile

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # supress ssl certificate warning, because I trust my own server

locations = "repo_locations.json"

class Client():

	def get_repo_path(self,id):
		return self.locations[str(id)]

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

	def pull_commit(self,commit_id,repo_id):
		FILE = "pulls/%s.zip"%repo_id
		r = self.get(["commits",commit_id])
		open(FILE,'wb').write(r.content)
		with ZipFile(FILE, 'r') as zipObj:
			zipObj.extractall(self.get_repo_path(repo_id))

def gen_commit(path):
	pass



if __name__ == '__main__':
	pass


import sys, json, requests, ssl
from urllib3.exceptions import InsecureRequestWarning
import os
from zipfile import ZipFile
from pathlib import Path
from winreg import *
import shutil
import re
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # supress ssl certificate warning, because I trust my own server

locations = "App/repo_locations.json"
TEMP = "App/commit.zip"
PULLS = "App/pulls"
MERGE = "App/merge"

class Duplicate(Exception):
	pass

class NoneSelected(Exception):
	pass

def get_downloads_folder():
	with OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders') as key:
		return QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]

class Control():

	def get_pull_path(self,id):
		return f"{PULLS}/{id}"

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
		self.get_session()
		with open(locations) as file:
			self.locations = json.load(file)

	def set_auth(self,auth):
		self.session.auth = auth

	def get_session(self):
		s = requests.Session()
		s.verify = False
		s.auth = ("User","Pass")
		self.session = s

	def get(self,path,params={}):
		return self.session.get(self.get_url(path),params=params)

	def post(self,path,params={}):
		return self.session.post(self.get_url(path),params=params)

	def ensure_in_pulls(self,commit_id):
		FILE = self.get_pull_path(commit_id)
		if not os.path.exists(FILE):
			r = self.get(["commits",commit_id])
			open(TEMP,'wb').write(r.content)
			with ZipFile(TEMP, 'r') as zipObj:
				zipObj.extractall(FILE)
		return FILE

	def pull_commit(self,commit_id,repo_id,to_working):
		pull = self.ensure_in_pulls(commit_id)
		path = self.get_repo_path(repo_id) if to_working else "%s/commit%s"%(get_downloads_folder(),commit_id)
		self.transfer_dir(pull,path)

	def transfer_dir(self,f,t):
		try:
			shutil.rmtree(t)
			shutil.copytree(f,t)
		except FileNotFoundError: 
			pass

	def set_location(self,repo_id,path):
		self.locations[str(repo_id)]=path
		with open(locations, 'w') as outfile:
			json.dump(self.locations, outfile)

	def zip(self,path):
		shutil.make_archive(TEMP.split(".")[0], 'zip', path)

	def commit(self,parent_id,repo,branch,name="",message=""):
		self.zip(self.get_repo_path(repo))
		r = self.session.post(self.get_url(["commits",parent_id]),files ={'file': open(TEMP, 'rb')}, \
			params={"Branch":branch,"Name":name,"Message":message} )

	def get_repo(self,id):
		return self.get(["repos",id])

	def get_profile(self):
		return self.get(["profile"])

	def get_users(self):
		return self.get(["users"]).json()

	def add_user_to_repo(self,repo,user):
		self.post(["add_user"],{"Repo":repo,"User":user})

	def fork(self,commit,branch_name):
		self.post(["fork"],{"Commit":commit,"Branch":branch_name})

	def create_repo(self,name):
		self.post(['create_repo'],{"Name":name})

	def setup_merge(self,Cto,Cfrom):
		self.ensure_in_pulls(Cto)
		self.ensure_in_pulls(Cfrom)

	def relative_path(self,path):
		return re.search(r"pulls/\d+/(.+)",path).groups()[0]

	def merge(self,paths,data_to,data_from):
		if len(paths)==0:
			raise NoneSelected

		relatives = list(map(self.relative_path,paths))

		if len(set(relatives))!=len(relatives): #relative has duplicates 
			raise Duplicate
		try:
			shutil.rmtree(MERGE)
		except FileNotFoundError:
			pass

		for i,path in enumerate(relatives):
			if "." in path: # file
				full_path = os.path.join(MERGE,path)
				directory = os.path.dirname(full_path)
				if not os.path.exists(directory):
					os.makedirs(directory)
				shutil.copyfile(paths[i],full_path)
			else: # directory
				shutil.copytree(paths[i],os.path.join(MERGE,path))

		self.zip(MERGE)
		r = self.session.post(self.get_url(["commits",data_to["id"]]),files ={'file': open(TEMP, 'rb')}, \
			params={"Branch":data_to["branch"]["id"],"Name":"Merged %s into %s"%(data_from["name"],data_to["name"]),"Message":" ","Merged":data_from["id"]} )
		print(data_to)
		self.transfer_dir(MERGE,self.get_repo_path(data_to["repo"]["id"]))

	def respond(self,id,response):
		self.post("response",{"Commit":id,"Response":response})




if __name__ == '__main__':
	pass


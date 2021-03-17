
import sqlite3 as lite
from cryptography.fernet import Fernet

import sys
sys.path.append(r'D:\Users\Guy\School\cyber\GuyHub\General')
from classes import *

class Crypto():
	def init_security(self):
		self.key = Fernet.generate_key()
		self.cipher_suite = Fernet(self.key)
		with open("key.txt","w") as f:
			f.write(self.key.decode())
	def get_security(self):
		with open("key.txt","r") as f:
			self.key = f.read()
			self.cipher_suite = Fernet(self.key)

	def decrypt(self,encrypted):
		return self.cipher_suite.decrypt(encrypted)
	def encrypt(self,data):
		return self.cipher_suite.encrypt(data.encode())


class Db():
	def __init__(self,path):
		self.path = path
		self.connect = lite.connect(self.path)

	def get_user(self,user_name):
		user_id  = self.fetch('''	SELECT Users.ID FROM Users WHERE Users.Name = "%s"'''%user_name)[0][0]
		return User(user_id,user_name)

	def execute(self,sql):
		cursor = self.connect.cursor()
		cursor.execute(sql)
		self.connect.commit()

	def fetch(self,sql):
		cursor = self.connect.cursor()
		cursor.execute(sql)
		return cursor.fetchall()

	def get_commits(self,condition):
		commits = self.fetch('''	SELECT Commits.ID, Commits.Name, Commits.Message, Commits.Parent, Branches.Name, Users.Name, Repos.Name
							From Commits JOIN Branches ON Branches.ID = Commits.Branch 
							JOIN Users ON Users.ID = Commits.User 
							JOIN Repos ON Repos.ID = Branches.Repo 
							WHERE %s'''% condition)
		return [Commit(commit[0],commit[1],commit[2],commit[3],commit[4],commit[5],commit[6]) for commit in commits]

	def validate(self, user, password):
		encrypted = self.fetch('''	SELECT Users.Name,Users.Password
							From Users 
							WHERE Users.Name="%s"'''%user.name)[0][1]
		actual = crypto.decrypt(encrypted.encode()).decode()
		return actual == password

	def set_password(self, user, password):
		encrypted = crypto.encrypt(password).decode()
		self.execute('''	UPDATE Users SET Password = "%s" WHERE Users.Name  = "%s"'''% (encrypted,user))

	def add_user(self, user_name, password):
		encrypted = crypto.encrypt(password).decode()
		self.execute('''	INSERT INTO Users (Name,Password) VALUES("%s","%s")'''%(user_name,encrypted))
		return self.get_user(user_name)

	def get_user_repos(self, user):
		repos = self.fetch('''	SELECT Repos.Name
							From Repos JOIN Connections ON Repos.ID = Connections.Repo 
							JOIN Users ON Users.ID = Connections.User WHERE Users.Name="%s"'''%user.name)
		return repos

	def add_user_to_repo(self, user, repo):

		self.execute('''	INSERT INTO Connections (Repo,User) VALUES("%s","%s")'''%(repo.id,user.id))

	def add_repo(self, owner, repo_name):
		self.execute('''	INSERT INTO Repos (Name) VALUES("%s")'''%(repo_name))
		repo = self.fetch('''	SELECT Repos.ID, Repos.Name From Repos ORDER BY ID DESC''')[0]
		repo = Repo(repo[0],repo[1])
		self.add_user_to_repo(owner,repo)
		branch = self.add_branch("Main",-1,owner,repo)
		self.add_commit("Init","Initial Commit",branch,-1,owner)
		return repo

	def add_branch(self, branch_name,parent,owner,repo):
		self.execute('''	INSERT INTO Branches (Name,Repo,Parent,Owner) 
			VALUES("%s","%s","%s","%s")'''%(branch_name,repo.id,parent,owner.id))
		branch = self.fetch('''	SELECT * From Branches ORDER BY ID DESC''')[0]
		return Branch(branch[0],branch[1],branch[3],branch[4],branch[2])

	def add_commit(self, commit_name, commit_message, branch,parent,user):
		if branch is Branch:
			self.execute('''	INSERT INTO Commits (Name,Branch,Parent,User,Message) 
				VALUES("%s","%s","%s","%s","%s")'''%(commit_name,branch.id,parent,user.id,commit_message))
		else:
			self.execute('''	INSERT INTO Commits (Name,Branch,Parent,User,Message) 
				VALUES("%s","%s","%s","%s","%s")'''%(commit_name,branch,parent,user.id,commit_message))

crypto = Crypto()
crypto.get_security()

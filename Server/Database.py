import sqlite3 as lite
from cryptography.fernet import Fernet

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


class Commit():
	def __init__(self,commit_id,name,message,parent_id,branch,user,repo):
		self.id = commit_id
		self.name = name
		self.message = message
		self.parent_id = parent_id
		self.branch = branch
		self.user = user
		self.repo = repo

class Db():
	def __init__(self,path):
		self.path = path
		self.connect = lite.connect(self.path)

	def get_commits(self,condition):
		cursor = self.connect.cursor()
		cursor.execute('''	SELECT Commits.ID, Commits.Name, Commits.Message, Commits.Parent, Branches.Name, Users.Name, Repos.Name
							From Commits JOIN Branches ON Branches.ID = Commits.Branch 
							JOIN Users ON Users.ID = Commits.User 
							JOIN Repos ON Repos.ID = Branches.Repo 
							WHERE %s'''% condition)
		commits = cursor.fetchall()
		return [Commit(commit[0],commit[1],commit[2],commit[3],commit[4],commit[5],commit[6]) for commit in commits]

	def validate(self, user, password):
		cursor = self.connect.cursor()
		cursor.execute('''	SELECT Users.Name,Users.Password
							From Users 
							WHERE Users.Name="%s"'''%user)
		encrypted = cursor.fetchall()[0][1]
		actual = crypto.decrypt(encrypted.encode()).decode()
		return actual == password

	def set_password(self, user, password):
		encrypted = crypto.encrypt(password).decode()
		cursor = self.connect.cursor()
		cursor.execute('''	UPDATE Users SET Password = "%s" WHERE Users.Name  = "%s"'''% (encrypted,user))
		self.connect.commit()

	def add_user(self,user,password):
		encrypted = crypto.encrypt(password).decode()
		cursor = self.connect.cursor()
		cursor.execute('''	INSERT INTO Users (Name,Password) VALUES("%s","%s")'''%(user,encrypted))
		self.connect.commit()


crypto = Crypto()
crypto.get_security()

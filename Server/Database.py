import sqlite3 as lite
from passlib.hash import pbkdf2_sha256


class Db():
	def __init__(self,path):
		self.path = path
		self.connect = lite.connect(self.path,check_same_thread=False)

	def is_commit_head_of_branch(self,commit,branch):
		branch_commits = self.fetch('''	SELECT Commits.Id FROM Commits WHERE Commits.branch = %s ORDER BY ID DESC'''%branch)
		return branch_commits[0][0]==commit

	def user_has_access(self,user_name,repo_id):
		res = self.fetch('''	SELECT * FROM Repos JOIN Connections ON Repos.Id = Connections.Repo 
						JOIN Users On Connections.User = Users.Id 
						WHERE Users.Name = "%s" AND Repos.Id = %s'''%(user_name,repo_id))
		return len(res)!=0

	def get_user(self,user_name):
		user_id  = self.fetch('''	SELECT Users.id FROM Users WHERE Users.Name = "%s"'''%user_name)[0][0]
		return {"id":user_id,"name":user_name}

	def user_exists(self,user_name):
		return self.fetch('''	SELECT * FROM Users WHERE Users.Name = "%s"'''%user_name)!=[]

	def get_repo(self, repo_id):
		repo = self.fetch('''SELECT Repos.Name FROM Repos WHERE Repos.id = %s'''%repo_id)[0]
		return {"id":repo_id,"name":repo[0]}
	
	def execute(self,sql):
		cursor = self.connect.cursor()
		cursor.execute(sql)
		self.connect.commit()

	def fetch(self,sql):
		cursor = self.connect.cursor()
		cursor.execute(sql)
		return cursor.fetchall()

	def get_commits(self,condition):
		commits = self.fetch('''	SELECT Commits.id, Commits.Name, Commits.Message, Commits.Parent, Branches.Name, Branches.id, Users.Name, Repos.Id, Commits.MergedFrom
							From Commits JOIN Branches ON Branches.id = Commits.Branch 
							JOIN Users ON Users.id = Commits.User 
							JOIN Repos ON Repos.id = Branches.Repo 
							WHERE Active = 1 AND %s'''% condition)
		return [{"id":commit[0],"name":commit[1],"message":commit[2],"parent":commit[3],"branch":{"name":commit[4],"id":commit[5]},"user":commit[6],"repo":self.get_repo(commit[7]),"mergedFrom":commit[8]} for commit in commits]

	def validate(self, user, password):
		stored = self.fetch('''	SELECT Users.Name,Users.Password
							From Users 
							WHERE Users.Name="%s"'''%user)[0][1]
		return pbkdf2_sha256.verify(password,stored)

	def set_password(self, user, password):
		encrypted = crypto.encrypt(password).decode()
		self.execute('''	UPDATE Users SET Password = "%s" WHERE Users.Name  = "%s"'''% (encrypted,user))

	def add_user(self, user_name, password):
		encrypted = pbkdf2_sha256.hash(password)
		self.execute('''	INSERT INTO Users (Name,Password) VALUES("%s","%s")'''%(user_name,encrypted))
		return self.get_user(user_name)

	def get_user_repos(self, user_name):
		repos = self.fetch('''	SELECT Repos.Name,Repos.ID
							From Repos JOIN Connections ON Repos.id = Connections.Repo 
							JOIN Users ON Users.id = Connections.User WHERE Users.Name="%s"'''%user_name)
		return [{"name": repo[0],"id":repo[1]} for repo in repos]

	def add_user_to_repo(self, user, repo):
		if len(self.fetch('''	SELECT * FROM Connections WHERE Connections.Repo = %s AND Connections.User = %s'''%(repo,user)))==0:
			self.execute('''	INSERT INTO Connections (Repo,User) VALUES("%s","%s")'''%(repo,user))

	def add_repo(self, owner, repo_name):
		self.execute('''	INSERT INTO Repos (Name) VALUES("%s")'''%(repo_name))
		repo = self.fetch('''	SELECT Repos.id, Repos.Name From Repos ORDER BY ID DESC''')[0]
		repo = {"id": repo[0],"name":repo[1]}
		self.add_user_to_repo(owner,repo["id"])
		branch = self.add_branch("Main",owner,repo["id"])
		self.add_commit("Init","Initial Commit",branch,-1,owner)
		return repo

	def add_branch(self, branch_name,owner,repo):
		self.execute('''	INSERT INTO Branches (Name,Repo,Owner) 
			VALUES("%s","%s","%s")'''%(branch_name,repo,owner))
		branch = self.fetch('''	SELECT * From Branches ORDER BY ID DESC''')[0]
		return branch[0]

	def get_repo_branches(self,repo_id):
		branches =  self.fetch('''	SELECT Branches.Name, Users.Name From Branches JOIN Users ON Branches.Owner = Users.ID WHERE Branches.Repo = %s'''%repo_id)
		return [{"name":branch[0], "owner":branch[1]} for branch in branches]

	def get_all_users(self):
		users =  self.fetch('''	SELECT Users.Name, Users.ID From Users''')
		return [{"name":user[0], "id":user[1]} for user in users]

	def get_repo_users(self,repo_id):
		users =  self.fetch('''	SELECT Users.Name, Users.ID From Users JOIN Connections ON Users.Id = Connections.User WHERE Connections.repo = %s'''%repo_id)
		return [{"name":user[0], "id":user[1]} for user in users]

	def get_newest_commit_id(self):
		commit = self.fetch('''	SELECT Commits.Id From Commits ORDER BY ID DESC''')[0]
		return commit[0]

	def add_commit(self, commit_name, commit_message, branch,parent,user,mergedFrom,active):
		if mergedFrom:
			self.execute('''	INSERT INTO Commits (Name,Branch,Parent,User,Message,MergedFrom,Active) 
								VALUES("%s","%s","%s","%s","%s","%s","%s")'''%(commit_name,branch,parent,user,commit_message,mergedFrom,active))
		else:
			self.execute('''	INSERT INTO Commits (Name,Branch,Parent,User,Message,Active) 
								VALUES("%s","%s","%s","%s","%s","%s")'''%(commit_name,branch,parent,user,commit_message,active))
		
	def get_branch_owner(self,id):
		return self.fetch('''SELECT Owner FROM Branches WHERE ID = %s'''%id)[0][0]

	def get_requests(self,repo_id):
		data  = self.fetch('''SELECT Commits.ID, Commits.Name, Commits.User, Branches.Owner FROM Commits JOIN Branches ON Branches.ID = Commits.Branch WHERE Active=0''')
		return [{"id":commit[0],"name":commit[1],"from":commit[2],"to":commit[3]} for commit in data]
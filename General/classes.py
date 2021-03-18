class Commit():
	def __init__(self,commit_id,name,message,parent_id,branch,branch_id,user,repo):
		self.idd = commit_id
		self.name = name
		self.message = message
		self.parent_id = parent_id
		self.branch = branch
		self.branch_id = branch_id
		self.user = user
		self.repo = repo

class User():
	def __init__(self,user_id,name):
		self.idd = user_id
		self.name = name

class Repo():
	def __init__(self,repo_id,name):
		self.idd = repo_id
		self.name = name

class Branch():
	def __init__(self,commit_id,name,parent_id,user,repo):
		self.idd = commit_id
		self.name = name
		self.parent_id = parent_id
		self.user = user
		self.repo = repo
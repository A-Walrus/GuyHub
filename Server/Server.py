import Database
import json,re,sys,os
from flask import Flask, make_response,jsonify,abort,request,send_file,send_from_directory,safe_join
from flask_httpauth import HTTPBasicAuth
from werkzeug.serving import WSGIRequestHandler
from zipfile import ZipFile

class Auth(HTTPBasicAuth):
	def name(self):
		return self.current_user()

	def id(self):
		return db.get_user(self.current_user())["id"]

db = Database.Db("GuyHub.db")

app = Flask(__name__)
auth = Auth()

app.config["commits"]=os.path.join(os.getcwd(),"commits")


def user_access_to_repo(username,repo_id):
	if db.user_has_access(username,repo_id):
		return True
	else:
		abort(403)

@auth.verify_password
def verify_password(username,password):
	if db.user_exists(username) and db.validate(username,password):
		return username

@app.route('/profile')
@auth.login_required
def profile():
	return {"user":db.get_user(auth.name()),"repos":db.get_user_repos(auth.name())}


@app.route('/create_repo', methods = ['POST'])
@auth.login_required
def create_repo():
	name = request.args.get("Name")
	db.add_repo(auth.id(),name)
	archive_name = os.path.join(app.config["commits"],"%s.zip"%db.get_newest_commit_id())
	with ZipFile(archive_name, 'w') as file:
	  pass
	return ""

@app.route("/repos/<int:repo_id>")
@auth.login_required
def repo(repo_id):
	if user_access_to_repo(auth.name(),repo_id):
		return {"commits":db.get_commits("Repos.ID = %s"%repo_id),"repo":db.get_repo(repo_id),"branches":db.get_repo_branches(repo_id),"users":db.get_repo_users(repo_id)}

@app.route("/add_user", methods = ['POST'])
@auth.login_required
def add_user():
	repo_id = request.args.get("Repo")
	user_id = request.args.get("User")
	if user_access_to_repo(auth.name(),repo_id):
		db.add_user_to_repo(user_id,repo_id)
		return ""

@app.route("/register", methods = ['POST'])
def register():
	username = request.args.get("User")
	password = request.args.get("Pass")
	if not db.user_exists(username):
		db.add_user(username,password)
		return ""
	else:
		abort(409)


@app.route("/fork", methods = ['POST'])
@auth.login_required
def fork():
	commit_id = request.args.get("Commit")
	branch_name = request.args.get("Branch")
	commit = db.get_commits("Commits.Id = %s"%commit_id)[0]
	repo_id = commit["repo"]["id"]
	if user_access_to_repo(auth.name(),repo_id):
		branch = db.add_branch(branch_name,auth.id(),repo_id)
		db.add_commit("Fork","",branch,commit_id,auth.id())
		id = db.get_newest_commit_id()

		with open(os.path.join(app.config["commits"],"%s.zip"%commit_id),'rb')as r:
			with open(os.path.join(app.config["commits"],"%s.zip"%id),'wb')as w:
				w.write(r.read())
		return ""


@app.route("/users")
@auth.login_required
def get_users():
	return {"users":db.get_all_users()}


@app.route("/commits/<int:commit_id>", methods = ["POST","GET"])
@auth.login_required
def commit(commit_id):
	commit = db.get_commits("Commits.Id = %s"%commit_id)[0]
	repo_id = commit["repo"]["id"]
	if user_access_to_repo(auth.name(),repo_id):
		if request.method == 'POST': # post
			args = request.args
			if db.is_commit_head_of_branch(commit_id,args.get("Branch")):
				db.add_commit(args.get("Name"),args.get("Message"),args.get("Branch"),commit_id,db.get_user(auth.name())["id"])
				id = db.get_newest_commit_id()
				file = request.files["file"]
				file.save(os.path.join(app.config["commits"],"%s.zip"%id))
				return ""
			else:
				abort(409)
		else: # get
			return send_from_directory(app.config["commits"], filename="%s.zip"%commit_id)
	

if __name__ == '__main__':
	WSGIRequestHandler.protocol_version = "HTTP/1.1" # http 1.1 -> allows keep alive
	app.run( debug=True,ssl_context=('selfsigned.crt', 'private.key')) 
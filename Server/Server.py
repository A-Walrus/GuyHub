import Database
import json,re
import ssl
from flask import Flask, make_response,jsonify,abort,request
from flask_httpauth import HTTPBasicAuth
from werkzeug.serving import WSGIRequestHandler
import sys

db = Database.Db("GuyHub.db")

app = Flask(__name__)
auth = HTTPBasicAuth()

def user_access_to_repo(username,repo_id):
	if db.user_has_access(username,repo_id):
		return True
	else:
		abort(401)


@auth.verify_password
def verify_password(username,password):
	if db.user_exists(username) and db.validate(username,password):
		return username

@app.route('/profile')
@auth.login_required
def profile():
	return {"user":db.get_user(auth.current_user()),"repos":db.get_user_repos(auth.current_user())}

@app.route("/repos/<int:repo_id>")
@auth.login_required
def repo(repo_id):
	if user_access_to_repo(auth.current_user(),repo_id):
		return {"commits":db.get_commits("Repos.ID = %s"%repo_id),"repo":db.get_repo(repo_id),"branches":db.get_repo_branches(repo_id)}
	else:
		abort(401)


@app.route("/commits/<int:commit_id>", methods = ["POST","GET"])
@auth.login_required
def commit(commit_id):
	commit = db.get_commits("Commits.Id = %s"%commit_id)[0]
	repo_id = commit["repo"]["id"]
	print(repo_id)
	if user_access_to_repo(auth.current_user(),repo_id):
		if request.method == 'POST': # post
			print(request)
		else: # get
			pass
		return {"borat":"great success"}
	

if __name__ == '__main__':
	WSGIRequestHandler.protocol_version = "HTTP/1.1" # http 1.1 -> allows keep alive
	app.run( debug=True,ssl_context=('selfsigned.crt', 'private.key'))
import Database
import json,re
import ssl
from flask import Flask, make_response,jsonify,abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.serving import WSGIRequestHandler

db = Database.Db("GuyHub.db")

app = Flask(__name__)
auth = HTTPBasicAuth()

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
	if repo_id in [repo["id"] for repo in db.get_user_repos(auth.current_user())]:
		return {"commits":db.get_commits("Repos.ID = %s"%repo_id),"repo":db.get_repo(repo_id),"branches":db.get_repo_branches(repo_id)}
	else:
		abort(401) # user doesn't have access to this repo

if __name__ == '__main__':
	WSGIRequestHandler.protocol_version = "HTTP/1.1" # http 1.1 -> allows keep alive
	app.run(ssl_context=('selfsigned.crt', 'private.key'))
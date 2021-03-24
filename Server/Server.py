import Database
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import re
from cryptography.fernet import Fernet, InvalidToken
import time

db = Database.Db("GuyHub.db")

key = Fernet.generate_key()
fernet = Fernet(key)

class Result():
	content_types = {
	"json":'application/json'
	}
	def __init__(self,content_type,byte_data):
		self.content_type = content_type
		self.byte_data = byte_data

	def run(self,request):
		request.send_response(200)
		request.send_header('Content-type', self.content_type)
		request.end_headers()
		request.wfile.write(self.byte_data)

class Serv(BaseHTTPRequestHandler):

	def get_user_token(self,user):
		return fernet.encrypt_at_time(user.encode(),int(time.time())).decode()

	def split(self):
		return self.path.split('/')[1::]

	def repos(self,path):
		print(self.path,self.user)
		if int(path[0]) in [repo["id"] for repo in db.get_user_repos(self.user)]:
			return Result('json',json.dumps({"commits":db.get_commits("Repos.ID=%s"%path[0]),"repo":db.get_repo(int(path[0]))}).encode())
		else:
			return Result('json',json.dumps({"error":"Access denied"}).encode())

	def users(self,path):
		pass

	def commits(self,path):
		pass

	def branches(self,path):
		pass

	def image(self,path):
		pass

	def do_GET(self):
		paths = {
				'repos': self.repos,
				'users': self.users,
				'commits': self.commits,
				'branches': self.branches
				}

		path = self.split()

		print(self.headers)
		if "token" in self.headers:
			self.token = self.headers["token"]
			try:
				self.user = fernet.decrypt(self.token.encode(),60*60).decode() # token valid for one hour
				if path[0] in paths:
					paths[path[0]](path[1::]).run(self)
			except InvalidToken:
				Result('json',json.dumps({"error":"InvalidToken"}).encode()).run(self)

		


	def login(self,data):
		data = json.loads(data.decode())
		if db.user_exists(data["name"]):
			if db.validate(data["name"],data["pass"]):
				return Result('json',json.dumps({"token":self.get_user_token(data["name"])}).encode()) 
			else:
				return Result('json',json.dumps({"error":"incorrect password"}).encode())
		else:
			db.add_user(data["name"],data["pass"])
			return Result('json',json.dumps({"token":self.get_user_token(data["name"])}).encode())


	def do_POST(self):
		paths = {
				'login' : self.login,
				}

		content_length = int(self.headers['Content-Length'])
		print(self.headers)
		post_data = self.rfile.read(content_length)
		path = self.split()
		if path[0] in paths:
			paths[path[0]](post_data).run(self)



	


httpd = HTTPServer(('localhost',8080),Serv)
httpd.socket = ssl.wrap_socket (httpd.socket, keyfile="private.key", certfile='selfsigned.crt', server_side=True)
httpd.serve_forever()


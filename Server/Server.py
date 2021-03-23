import Database
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import re

db = Database.Db("GuyHub.db")

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

	def repos(self,path):
		print(self.path)
		return Result('json',json.dumps({"commits":db.get_commits("Repos.ID=%s"%path[0]),"repo":db.get_repo(int(path[0]))}).encode())

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

		path = self.path.split('/')[1::]
		if path[0] in paths:
			paths[path[0]](path[1::]).run(self)

	


httpd = HTTPServer(('localhost',8080),Serv)
httpd.socket = ssl.wrap_socket (httpd.socket, keyfile="private.key", certfile='selfsigned.crt', server_side=True)
httpd.serve_forever()


import Database
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

db = Database.Db("GuyHub.db")

class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		print(self.path)
		self.send_response(200)
		self.end_headers()
		self.wfile.write(json.dumps(db.get_commits("Repos.ID=1")).encode())

httpd = HTTPServer(('10.0.0.23',8080),Serv)
httpd.serve_forever()


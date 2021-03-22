import Database
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

db = Database.Db("GuyHub.db")

class Serv(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		self.wfile.write(json.dumps(db.get_commits("Repos.ID=1")).encode())

httpd = HTTPServer(('0.0.0.0',8080),Serv)
httpd.socket = ssl.wrap_socket (httpd.socket, keyfile="private.key", certfile='selfsigned.crt', server_side=True)
httpd.serve_forever()


from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
from http.client import HTTPSConnection
import ssl

from ui import *


def main():
	app = QApplication(sys.argv)
	file = QFile("theme.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())


	connection = HTTPSConnection("localhost:8080 ",context=ssl._create_unverified_context())
	foo = {'name': 'Elon','pass':'$TSLA'}
	json_data = json.dumps(foo)

	connection.request("POST","/login",json_data,{'Content-type': 'application/json'})
	response = connection.getresponse()
	token = json.loads(response.read().decode())["token"]
	
	# token = "gAAAAABgWkeEiO_gAmi-tmS4YF_ImH8IkALN7xZA993BtHaqaHc_zZ3Dfe-I8wQJ5cJkwmSJ6t5UCn3wFkokUmI0N2KyllQikQ=="

	connection.request("GET","/repos/1",None,{'token':token})
	response = connection.getresponse()
	data = response.read().decode()

	connection.close()
	
	print(json.loads(data))
	win = RepoView(json.loads(data))
	
	sys.exit(app.exec_())


if __name__ == '__main__':
    main()
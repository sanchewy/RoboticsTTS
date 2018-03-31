import socket
import subprocess

class clientSocket():
	def __init__(self, ipAddress, port):
		print("CREATED SOCKET " + ipAddress + " " + port)
		# create a socket object
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# connection to hostname on the port.
		self.socket.connect((ipAddress, int(port)))

	def sendMessage(self, message):
		self.socket.send((message).encode('ascii'))

	def run(self):
		#Basically this does nothing other than keep the socket alive
		pass
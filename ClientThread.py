import socket
import subprocess
import threading

class clientSocket():
	def __init__(self, ipAddress, port):
		# self.thread = threading.Thread(target=self.sendMessage, args=())
		# self.message = ""
		print("CREATED SOCKET " + ipAddress + " " + str(port-1))
		# create a socket object
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# connection to hostname on the port.
		self.socket.connect((ipAddress, port-1))
		# self.socket.connect(('"10.200.0.98"', port))

	def sendMessage(self, message):
		self.socket.send((message).encode('ascii'))
		print("**************sent message**********")

	def run(self):
		#Basically this does nothing other than keep the socket alive
		pass
import socket
import re

class servSocket():
    def __init__(self, port):
        # create a socket object
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # get local machine name
        self.host = socket.gethostname()
        self.port = port
        # bind to the port
        self.serversocket.bind((self.host, self.port))
        # queue up to 5 requests
        self.serversocket.listen(5)

    def run(self):
        # establish a server connection
        clientsocket,addr = self.serversocket.accept()
        print("Got a connection from %s" % str(addr))

        while True:
            # Receive message from android phone
            data = clientsocket.recv(1024).decode("ascii")
            pattern = re.compile(".*start.*")    #This should match all phrases with the word "start" in them
            if data:
                print("Server Data: " + data + " Match: " + str(bool(re.search(pattern, data))))
                if bool(re.search(pattern, data)):
                    import gui
                    print("Server thread starting gui instruction execution.")
                    gui.start_drawing()
        
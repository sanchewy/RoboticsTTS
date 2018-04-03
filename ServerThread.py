import socket
import re
from multiprocessing import Queue

class servSocket():
    def __init__(self, port, guiInst, outputQueue):
        # create a socket object
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # get local machine name
        self.host = socket.gethostname()
        self.port = port
        self.guiInst = guiInst      
        # bind to the port
        self.serversocket.bind((self.host, self.port))
        # queue up to 5 requests
        self.serversocket.listen(5)
        self.outputQueue = outputQueue

    def run(self):
        while True:
            # establish a server connection
            clientsocket,addr = self.serversocket.accept()
            print("Got a connection from %s" % str(addr))

            while True:
                # Receive message from android phone
                data = clientsocket.recv(1024).decode("ascii")
                startpattern = re.compile(".*start.*")    #This should match all phrases with the word "start" in them
                homepattern = re.compile(".*go home.*")
                spinpattern = re.compile(".*spin circle.*")
                if data:
                    print("Server Data: " + data + " Start Match: " + str(bool(re.search(startpattern, data))) + "\n\t Go Home Match: " + str(bool(re.search(homepattern, data))) + "\n\t Circle Match: " + str(bool(re.search(spinpattern, data))))
                    if bool(re.search(startpattern, data)):
                        import gui
                        print("Server thread starting gui instruction execution.")
                        self.guiInst.start_drawing()
                    elif bool(re.search(homepattern, data)):
                        self.outputQueue.put("GoHome")
                    elif bool(re.search(spinpattern, data)):
                        self.outputQueue.put("SpinCircle")
                    else:
                        print("Error: The speech to text was not recognized as a valid command.")
                else:
                    break
            clientsocket.close()
        
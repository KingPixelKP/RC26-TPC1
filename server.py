"""
67775   Gab
68130   Dinis Neves
"""
from socket import *
import threading
import time
import os


# Start Server
SERVER_RUNNING = "Server is running"
SERVER_NOT_START = "Unable to start server"

# Recieve client
WELCOME_CLIENT1 = "Welcome to "
WELCOME_CLIENT2 = " file server"

#ERR
FILE_NOT_FOUND = "File not found"




serverPort = 12000
socketBuffer = 1024


# Function to handle client, called always with a new threaded
def handle_client(c):
  while True:
    data = c.recv(1024)
    dataD = data.decode()
    if not dataD:
      print('Bye')
      break
    time.sleep(5)
    print("received from client: ", dataD)    
    c.send(data)
  c.close()



def main():

    # Welcoming socket and listen for requests
    host = ''
    port = 12345
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(("", serverPort))
    serverSocket.listen(5)
    print("Server running on port", port)




    while True:



        # Thread to recieve new clients
        c, addr = serverSocket.accept()
        print('Connected to:', addr[0], ':', addr[1])
        tid = threading.Thread(target=handle_client, args = (c,))
        
        # KeyBoardInterrupt
        try:
            print(".", end=' ',flush=True)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting!")
            break
        print("Ending ")



main()
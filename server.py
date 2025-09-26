"""
67775   Gab
68130   Dinis Neves
"""
from socket import *
import threading
import time
import os
import pickle

serverPort : int = 12000
socketBuffer : int = 1024
SIZE : int = 512


## Start Server
SERVER_RUNNING : str = "Server is running"
SERVER_NOT_START : str = "Unable to start server"

## Recieve client
WELCOME_CLIENT1 : str = "Welcome to "
WELCOME_CLIENT2 : str = " file server"

## Errors
FILE_NOT_FOUND : str = "File not found"


## OP Codes
REQUET_FILE_OP : int = 1
DATA_OP : int = 3
ACKNOWLEDGE_OP : int = 4






def send_acknowledge_block(block : int, socket : socket):
    acknowledge = (ACKNOWLEDGE_OP, block)
    ack = pickle.dumps(acknowledge)
    socket.send(ack)




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


# Function to do the dir command
def dir_command():
   dir_path = "."
   dir_list = os.listdir(dir_path)
      ## send to client
    
   for x in dir_list:
      print(x)


# Function to do the get command server side
def get_command(fName):
    try: 
      f = open(fName, "rb")
    except:
       print(FILE_NOT_FOUND)
    
    data = f.read(SIZE)
    while (data):
       ## send to client
       sdata : tuple = (DATA_OP, data)
       ssdat = pickle.dumps(sdata)
       socket.send(ssdat)


## end ???
'''client closes socket but  server keep going'''
   



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
        
        break
    
main()
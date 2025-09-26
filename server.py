"""
67775   Gabriel Matias
68130   Dinis Neves
"""
from socket import *
import threading
import time
import os
import pickle

serverPort : int = 12000
SOCKET_BUFFER : int = 1024
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
ERROR_OP : int = 5

def close_program(socket : socket):
    socket.close()
    exit()

def send_acknowledge_block(block : int, socket : socket):
    acknowledge = (ACKNOWLEDGE_OP, block)
    ack = pickle.dumps(acknowledge)
    socket.send(ack)

def recv_acknowledge_block(block : int, socket : socket):
    ack = socket.recv(SOCKET_BUFFER)
    (op_code, acknowledged_block) = pickle.loads(ack)

    if op_code == ERROR_OP:
        recv_error(ack, socket)

    if acknowledged_block != block:
        print("Wrong block acknowledged: ACK")

def recv_error(req : bytes, socket : socket):
    (_, error_string) = pickle.loads(req)
    print(error_string)
    close_program()


def send_data_block(block : int, size : int, data : str, socket : socket):
   data_tuple = (DATA_OP, block, size, data)
   dat = pickle.dumps(data_tuple)
   socket.send(dat)
   

def recv_request(socket : socket) -> str:
    rec = socket.recv(SOCKET_BUFFER)
    (op_code, file_name) = pickle.loads(rec)

    if op_code == ERROR_OP:
        recv_error(rec, socket)
    return file_name





# Function to handle client, called always with a new threaded
def handle_client(socket : socket):
  while True:
    file_name = recv_request(socket)

    if file_name == "":
      dir_command(socket)
    else:
      get_command(file_name, socket)


# Function to do the dir command
def dir_command(socket : socket):
  dir_path = "."
  dir_list = os.listdir(dir_path)

      ## send to client
  block = 0
  for x in dir_list:
     send_data_block(block, len(x), x, socket)
     recv_acknowledge_block(block, socket)
     block = block + 1
     break
  send_data_block(block, 0, "", socket)
  recv_acknowledge_block(block, socket)

  
  
  
   


# Function to do the get command server side
def get_command(fName : str, socket : socket):
    try: 
      f = open(fName, "r")
    except:
       print(FILE_NOT_FOUND)
    
    data = f.read(SIZE)
    block = 0
    while (data):
      send_data_block(block, len(data), data, socket)
      recv_acknowledge_block(block, socket)
      block = block + 1
      data = f.read(SIZE)
    


       
 


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
        socket, addr = serverSocket.accept()
        print('Connected to:', addr[0], ':', addr[1])
        tid = threading.Thread(target=handle_client, args = (socket,))
        
        break
    
main()
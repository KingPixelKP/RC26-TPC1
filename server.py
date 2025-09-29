"""
67775   Gabriel Matias
68130   Dinis Neves
"""

import threading
import os
import pickle
import sys
import socket as s
from socket import *

serverPort : int = 12000
SOCKET_BUFFER : int = 1024
SIZE : int = 512


## Start Server
SERVER_RUNNING : str = "Server is running"
SERVER_NOT_START : str = "Unable to start server"

## Recieve client
WELCOME_CLIENT : str = "Welcome to {} file server"

## Errors
FILE_NOT_FOUND : str = "ERROR: File not found"
PROTOCOL_ERR : str = "ERROR: Protocol Error connection closed: Unexpected Op_code, expected -> {}, found -> {}"
ACKNOWLEDGE_ERR : str = "ERROR: Incorrect Acknowledge packet, expected -> {}; found -> {}"

USER_INTERRUPT : str = "\nProgram interrupted by user closing connection."


## OP Codes
REQUET_FILE_OP : int = 1
DATA_OP : int = 3
ACKNOWLEDGE_OP : int = 4
ERROR_OP : int = 5



### Protocol
FILE_NOT_FOUND : str = "ERROR: File not found"
PROTOCOL_ERR : str = "ERROR: Protocol Error connection closed: Unexpected Op_code, expected -> {}, found -> {}"
ACKNOWLEDGE_ERR : str = "ERROR: Incorrect Acknowledge packet, expected -> {}; found -> {}"


def close_program(socket : socket):
    socket.close()
    exit()

def send_acknowledge_block(block : int, socket : socket):
    acknowledge = (ACKNOWLEDGE_OP, block)
    ack = pickle.dumps(acknowledge)
    socket.send(ack)


def send_error_block(error : str, socket : socket):
  err = pickle.dumps((ERROR_OP, error))
  socket.send(err)


def send_data_block(block : int, size : int, data : str, socket : socket):
  data_tuple = (DATA_OP, block, size, data)
  dat = pickle.dumps(data_tuple)
  socket.send(dat)
   
def send_request(file_name : str, socket : socket):
    request : tuple = (REQUET_FILE_OP, file_name)
    req = pickle.dumps(request)
    socket.send(req)

def recv_error(req : bytes, socket : socket):
    (_, error_string) = pickle.loads(req)
    print(error_string)
    close_program(socket)

def recv_acknowledge_block(block : int, socket : socket):
  ack = socket.recv(SOCKET_BUFFER)
  tuple = pickle.loads(ack)

  op_code = tuple[0]

  if op_code == ERROR_OP:
    recv_error(ack, socket)
  
  if op_code != ACKNOWLEDGE_OP:
     send_error_block(PROTOCOL_ERR.format(ACKNOWLEDGE_OP, op_code), socket)

  (op_code, acknowledged_block) = pickle.loads(ack)

  if acknowledged_block != block:
    send_error_block(ACKNOWLEDGE_ERR.format(block, acknowledged_block), socket)


def recv_data(socket : socket) -> tuple[int, int, int , bytes]:
    req = socket.recv(SOCKET_BUFFER)
    tuple = pickle.loads(req)

    op_code = tuple[0]

    if op_code == ERROR_OP:
        recv_error(req, socket)

    if op_code != DATA_OP:
      send_error_block(PROTOCOL_ERR.format(DATA_OP, op_code), socket)

    return pickle.loads(req)

def recv_request(socket : socket) -> str:
    req = socket.recv(SOCKET_BUFFER)    
    tuple = pickle.loads(req)

    op_code = tuple[0]

    if op_code == ERROR_OP:
        recv_error(req, socket)

    if op_code != REQUET_FILE_OP:
      send_error_block(PROTOCOL_ERR.format(REQUET_FILE_OP, op_code), socket)

    (_, file_name) = pickle.loads(req)

    return file_name


### End of Protocol



## Server Functions

# Function to handle client, called always with a new threaded
def handle_client(socket : socket, client_address : str, server_address : str):
  try:
    welcome_message = WELCOME_CLIENT.format(server_address)
    send_data_block(0, len(welcome_message), welcome_message, socket)
    recv_acknowledge_block(0, socket)
    while True:
      file_name = recv_request(socket)

      if file_name == "":
        dir_command(socket)
      else:
        get_command(file_name, socket)
  except EOFError:
     print("Client: {} has disconected or suffered an error".format(client_address))
  except BrokenPipeError:
     print("Client: {} has disconected or suffered an error".format(client_address))
     
    


# Function to do the dir command
def dir_command(socket : socket):
  dir_path = "."
  dir_list = os.listdir(dir_path)

      ## send to client
  block = 0
  for x in dir_list:

    if os.path.isfile(x):
      send_data_block(block, len(x), x, socket)
      recv_acknowledge_block(block, socket)
      block = block + 1

  send_data_block(block, 0, "", socket)
  recv_acknowledge_block(block, socket)


# Function to do the get command server side
def get_command(fName : str, socket : socket):
    try: 
      f = open(fName, "rb")
      block = 0


      while True:
        data = f.read(SIZE)
        send_data_block(block, len(data), data, socket)
        recv_acknowledge_block(block, socket)
        block = block + 1
        if not data or len(data) < SIZE:
           break
          
         

    except OSError:
       send_error_block(FILE_NOT_FOUND, socket)


def main():
  serverSocket = s.socket(AF_INET,SOCK_STREAM)
  try:

    serverSocket.bind(("", int(sys.argv[1])))
  
    serverSocket.listen(5)
    print("Server running on port {}, {}".format(sys.argv[1], serverSocket.getsockname()))
    while True:
        # Thread to recieve new clients
        socket, addr = serverSocket.accept()
        print('Connected to:', addr[0], ':', addr[1])
        tid = threading.Thread(target=handle_client, args = (socket, addr[0], serverSocket.getsockname()[0]))
        tid.start()
  except KeyboardInterrupt:
      print(USER_INTERRUPT)
      close_program(serverSocket)

if __name__ == "__main__":
    main()

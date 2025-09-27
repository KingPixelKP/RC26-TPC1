import pickle
from socket import *

SOCKET_BUFFER : int = 1024
SIZE : int = 512


## Start Server
SERVER_RUNNING : str = "Server is running"
SERVER_NOT_START : str = "Unable to start server"

## Errors
FILE_NOT_FOUND : str = "ERROR: File not found"
PROTOCOL_ERR : str = "ERROR: Protocol Error connection closed"
ACKNOWLEDGE_ERR : str = "ERROR: Incorrect Acknowledge packet, expected -> {}; found -> {}"


## OP Codes
REQUET_FILE_OP : int = 1
DATA_OP : int = 3
ACKNOWLEDGE_OP : int = 4
ERROR_OP : int = 5

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
  close_program(socket)


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

import pickle
from socket import *
import sys
import os

PROMPT : str = "client>"
SOCKET_BUFFER : int = 1024



## Commands
GET_CMD : str = "get"
DIR_CMD : str = "dir"
END_CMD : str = "end"

## Success
SUCCESS_CONNECT = "Connect to server"


## Errors
ARGV_ERR : str = "Correct usage -> python3 client.py <server_address> <server_port>"

GET_ERR1 : str = "Invalid number of arguments!!!\nCorrect usage -> get <server file name> <copied file name>"
GET_ERR2 : str = "A file with the indicated name already exists on the client!!!"
GET_ERR3 : str = "The indicated file does not exist on the server!!!"

UNK_CMD_ERR : str = "Unkwown command"

FAILED_CONNECT : str = "Unable to connect with the server"

USER_INTERRUPT : str = "\nProgram interrupted by user closing connection."

PROTOCOL_ERR : str = "ERROR: Protocol Error connection closed"
ACKNOWLEDGE_ERR : str = "ERROR: Incorrect Acknowledge packet, expected -> {}; found -> {}"

## OP Codes
REQUET_FILE_OP : int = 1
DATA_OP : int = 3
ACKNOWLEDGE_OP : int = 4
ERROR_OP : int = 5

### Protocol
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

### End of Protocol




def get_command(line : str, client_socket : socket):
    if (len(line.split()) != 3):
        print(GET_ERR1)
        return
    
    server_file : str = line.split()[1]
    client_file : str = line.split()[2]

    if (os.path.isfile(client_file)):
        print(GET_ERR2)
        return

    send_request(server_file, client_socket)
    
    file = open(client_file, "w")

    expected_block = 0

    while True:
        (_, block, size, data) = recv_data(client_socket)
        
        if expected_block != block:
            send_error_block(PROTOCOL_ERR, client_socket)
            print(PROTOCOL_ERR)
            close_program(client_socket)
            
        send_acknowledge_block(block, client_socket)
        file.write(data)
        expected_block = expected_block + 1
        if size < 512:
            break
        
    file.close()

def dir_command(client_socket : socket):

    send_request("", client_socket)

    while True:
        (_, block, size, data) = recv_data(client_socket)
        send_acknowledge_block(block, client_socket)
        if size == 0:
            break
        print(data)
    

def main():
    client_socket = socket(AF_INET,SOCK_STREAM)
    try: 
        if len(sys.argv) < 3:
            print(ARGV_ERR)
            exit()

        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])


        client_socket.connect((server_ip, server_port))

        (_, block, _, welcome_message) = recv_data(client_socket)
        send_acknowledge_block(block, client_socket)

        print(SUCCESS_CONNECT)
        print(welcome_message)

        line : str
        cmd : str

        while True:
            line = input(PROMPT)

            if line == "":
                print(UNK_CMD_ERR)
            else:
                cmd = line.split()[0]

                if cmd == GET_CMD:
                    get_command(line, client_socket)
                elif cmd == DIR_CMD:
                    dir_command(client_socket)
                elif cmd == END_CMD:
                    break
                else:
                    print(UNK_CMD_ERR)
        

    except KeyboardInterrupt:
        print(USER_INTERRUPT)
        close_program(client_socket)
    except ConnectionRefusedError:
        print(FAILED_CONNECT)

if __name__ == "__main__":
    main()








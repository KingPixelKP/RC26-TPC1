import pickle
from socket import *
import sys

PROMPT : str = "client>"
SOCKET_BUFFER : int = 1024



## Commands
GET_CMD : str = "get"
DIR_CMD : str = "dir"
END_CMD : str = "end"



## Errors
ARGV_ERR : str = "Correct usage -> python3 client.py <server_address> <server_port>"

GET_ERR1 : str = "Invalid number of arguments!!!\nCorrect usage -> get <server file name> <copied file name>"
GET_ERR2 : str = "A file with the indicated name already exists on the client!!!"
GET_ERR3 : str = "The indicated file does not exist on the server!!!"

USER_INTERRUPT : str = "\nProgram interrupted by user closing connection."

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

def send_request(file_name : str, socket : socket):
    request : tuple = (REQUET_FILE_OP, file_name)
    req = pickle.dumps(request)
    socket.send(req)

def recv_error(req : bytes, socket : socket):
    (_, error_string) = pickle.loads(req)
    print(error_string)
    close_program()


def recv_acknowledge_block(block : int, socket : socket):
    ack = socket.recv(SOCKET_BUFFER)
    (op_code, acknowledged_block) = pickle.loads(ack)

    if op_code == ERROR_OP:
        recv_error(ack, socket)

    if acknowledged_block != block:
        print("Wrong block acknowledged: ACK")

def recv_data(socket : socket) -> tuple[int, int, int , bytes]:
    req = socket.recv(SOCKET_BUFFER)
    (op_code, _, _, _) = pickle.loads(req)

    if op_code == ERROR_OP:
        recv_error(req, socket)

    return pickle.loads(req)

def get_command(line : str, client_socket : socket):
    if (len(line.split()) != 3):
        print(GET_ERR1)
    
    server_file : str = line.split()[1]
    client_file : str = line.split()[2]

    send_request(server_file, client_socket)
    
    message_size : int
    (_, block, _, message_size_data) = recv_data(client_socket)
    send_acknowledge_block(block, client_socket)
    message_size = int(message_size_data)

    received_size : int = 0

    file = open(client_file, "wb")

    while received_size < message_size:
        (_, block, size, data) = recv_data(client_socket)
        send_acknowledge_block(block, client_socket)
        file.write(data)
        received_size = received_size + size
        
    file.close()

def dir_command(client_socket : socket):

    file_size : int
    (_, block, _, file_size_data) = recv_data(client_socket)
    send_acknowledge_block(block, client_socket)
    file_size = int(file_size_data)

    received_size : int = 0

    while received_size < file_size:
        (_, block, size, data) = recv_data(client_socket)
        send_acknowledge_block(block, client_socket)
        print(data)
        received_size = received_size + size
    

def main():
    try: 
        if len(sys.argv) < 3:
            print(ARGV_ERR)
            exit()

        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])

        client_socket = socket(AF_INET,SOCK_STREAM)

        client_socket.connect((server_ip, server_port))

        (_, block, _, welcome_message) = recv_data(client_socket)
        send_acknowledge_block(block, client_socket)

        print("Connect to server")
        print(welcome_message)

        line : str
        cmd : str

        while True:
            line = input(PROMPT)
            cmd = line.split()[0]

            if cmd == GET_CMD:
                get_command(line, client_socket)
            elif cmd == DIR_CMD:
                dir_command(client_socket)
            elif cmd == END_CMD:
                break
        

    except KeyboardInterrupt:
        close_program()

if __name__ == "__main__":
    main()








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

def send_acknowledge_block(block : int, socket : socket):
    acknowledge = (ACKNOWLEDGE_OP, block)
    ack = pickle.dumps(acknowledge)
    socket.send(ack)

def send_request(file_name : str, socket : socket):
    request : tuple = (REQUET_FILE_OP, file_name)
    req = pickle.dumps(request)
    socket.send(req)


def get_command(line : str, client_socket : socket):
    if (len(line.split()) != 3):
        print(GET_ERR1)
    
    server_file : str = line.split()[1]
    client_file : str = line.split()[2]

    send_request(server_file, client_socket)
    
    file_size : int
    file_size =  int(client_socket.recv(SOCKET_BUFFER).decode())

    received_size : int = 0

    file = open(client_file, "wb")

    while received_size < file_size:
        req = client_socket.recv(SOCKET_BUFFER)
        (op_code, block, size, data) = pickle.loads(req)

        if op_code != DATA_OP:
            print("Error")
        
        send_acknowledge_block(block, client_socket)

        file.write(data)
        received_size = received_size + size
        
    file.close()


def main():
    try: 
        if len(sys.argv) < 3:
            print(ARGV_ERR)
            exit()

        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])

        client_socket = socket(AF_INET,SOCK_STREAM)

        #client_socket.connect((server_ip, server_port))

        #welcome_message = client_socket.recv().decode()

        print("Connect to server")
        #print(welcome_message)

        line : str
        cmd : str

        while True:
            line = input(PROMPT)
            cmd = line.split()[0]

            if cmd == GET_CMD:
                get_command(line, client_socket)
            elif cmd == DIR_CMD:
                pass
            elif cmd == END_CMD:
                break


    except KeyboardInterrupt:
        print(USER_INTERRUPT)

if __name__ == "__main__":
    main()








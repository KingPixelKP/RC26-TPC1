import pickle
from socket import *
import sys

PROMPT : str = "client>"

GET_CMD : str = "get"
DIR_CMD : str = "dir"
END_CMD : str = "end"

GET_ERR1 : str = "Invalid number of arguments!!!"
GET_ERR2 : str = "A file with the indicated name already exists on the client!!!"
GET_ERR3 : str = "The indicated file does not exist on the server!!!"

def main():

    host_ip = sys.argv[1]
    host_port = sys.argv[2]

    client_socket = socket(AF_INET,SOCK_STREAM)

    


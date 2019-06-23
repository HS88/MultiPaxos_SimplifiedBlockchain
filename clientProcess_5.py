from Client_Main import *
from Configuration import *
import sys

if __name__ == "__main__":
    server_ip = 'localhost'
    server_port = 8130
    client_ip = 'localhost'
    client_port = 8132

    id = int(sys.argv[1])
    client_con = ServerConfig.client_list[ id ].split(",")
    server_con = ServerConfig.server_list[ id ].split(",")
    server_ip = server_con[0]
    server_port = int(server_con[1])
    client_ip = client_con[0]
    client_port = int(client_con[1])
    client = Client('E', client_ip, client_port, server_ip, server_port, 3 )
    client.startClient()
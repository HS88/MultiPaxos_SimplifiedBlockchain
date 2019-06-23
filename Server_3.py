from Server_Main import *
import os
from Configuration import *

if __name__ == '__main__':

  print(os.path.abspath(__file__))
  '''
  otherServers = {'A': "localhost,8080", 'C': "localhost,8090"}
#  otherServers = {'A': "localhost,8080", 'B': "localhost,8090", 'D': "localhost,8110", 'E': "localhost,8120"}

  id = 3
  ip = 'localhost'
  port = 8100
  client_IP = 'localhost'
  client_port = 8102
  '''
  id = int(sys.argv[1])

  otherServers = ServerConfig.other_server_list[ id ]
  server_parameters = ServerConfig.server_list[ id ].split(',')
  ip = server_parameters[0]
  port = int(server_parameters[1])
  client_config = ServerConfig.client_list[ id ].split(',')
  client_IP = client_config[0]
  client_port = int(client_config[1])

  networkPartition = ServerConfig.networkPartioned
  partitionCounter=ServerConfig.partitionTimerCount
  partitionTimer = ServerConfig.partitionTimer

  blockchain_received = False
  if(id == 3):
    ans = int( sys.argv[2] )
    if(ans == 1):
      blockchain_received = False
    elif(ans == 2):
      blockchain_received = True

  loadState = ServerConfig.loadState
  server = Server(id, ip, port, client_IP, client_port, otherServers, blockchain_received=blockchain_received, loadState=loadState,
                  networkPartition=networkPartition,partitionTimer=partitionTimer, partitionCounter=partitionCounter )

#  server = Server(id, ip, port, client_IP, client_port, otherServers)
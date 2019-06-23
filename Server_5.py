from Server_Main import *
import os
from Configuration import *

if __name__ == '__main__':

  print(os.path.abspath(__file__))
  '''
  otherServers = {'A': "localhost,8090", 'C': "localhost,8100"}
  otherServers = {'A': "localhost,8080", 'B': "localhost,8090", 'C': "localhost,8100", 'D': "localhost,8110"}
#  otherServers = {
  id = 5
  ip = 'localhost'
  port = 8120
  client_IP = 'localhost'
  client_port = 8122
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
  if(id == 5):
    ans = int( sys.argv[2] )
    if(ans == 1):
      blockchain_received = False
    elif(ans == 2):
      blockchain_received = True


#    ans = int(sys.argv[3])

  loadState = ServerConfig.loadState
  server = Server(id, ip, port, client_IP, client_port, otherServers, blockchain_received = True, loadState=loadState,
                  networkPartition=networkPartition,partitionTimer=partitionTimer, partitionCounter=partitionCounter )

 # server = Server(id, ip, port, client_IP, client_port, otherServers)
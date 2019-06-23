import sys, socket, threading, pickle, time, random
from Block import printBlock, Block
from paxosMessage import *
from handleMessages import Acceptor, Leader
from time import sleep
import random
import datetime
from Configuration import *
import os.path

class ServerState(object):
  def __init__(self,blockchain, ballotNum, tempTxns):
    self.blockchain = blockchain
    self.ballotNum = ballotNum
    self.tempTxns = tempTxns

class ServerUtilities(object):
  @staticmethod
  def isOpen(ip, port):
    alive = False
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((ip, port))
      s.shutdown(socket.SHUT_RDWR)
      alive = True
    except:
      alive = False
    return alive

  @staticmethod
  def getBalanceForAll( blockchain ):
    bal = [100]*5
    for block in blockchain:
      for txn in block.txns:
        sender, receiver, amount = txn.split(' ')
        s = ord(sender) - ord('A')
        r = ord(receiver) - ord('A')
        bal[s] = bal[s] - int(amount)
        bal[r] = bal[r] + int(amount)
    result = "\nBalance of A: " + str(bal[0]) + "\nBalance of B: " + str(bal[1]) + "\nBalance of C: " + str(bal[2]) + "\nBalance of D: " + str(bal[3]) + "\nBalance of E: " + str(bal[4])
    return result

  @staticmethod
  def replyToClient( client_connection, message ):
#    print("NODE - Reply to client")
    sock_send_to_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_address = ( client_connection )
    sock_send_to_client.connect( client_address )

    try:
      sock_send_to_client.sendall(pickle.dumps( message ))
    except:
      print("Exception occurred while sending data to client")
    finally:
      sock_send_to_client.shutdown(socket.SHUT_RDWR)
      sock_send_to_client.close()

  @staticmethod
  def sendMessage_Thread(message):
    delay = ServerConfig.serverToServerDelay
    delay = random.randrange( delay[0],delay[1] )
    socketThread = threading.Thread( target=ServerUtilities.sendMessage, args=( message, delay ))
    socketThread.start()

  @staticmethod
  def sendMessage( message, delay=1 ):
#    print("NODE- Sending message")
#    print(delay)
#    print(datetime.datetime.now())
    sleep(delay)
#    print(datetime.datetime.now())
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ( message.receiver )
    exception = True
    try:
      sock.connect(server_address)
      sock.sendall(pickle.dumps(message))
      sock.shutdown(socket.SHUT_RDWR)
    except:
      exception = False
      print("Exception occurred while sending data to server")
      return "Exception occurred while sending data to server"
    finally:
      sock.close()
    return exception

  @staticmethod
  def getTransactionsFromBlockchain( blockchain ):
    commitedTxns = []
    for block in blockchain:
      commitedTxns.append(block.txns[0])
      commitedTxns.append(block.txns[1])
    return commitedTxns

class Server(object):
  def __init__(self, id, ip, port, client_ip, client_port, otherServers, blockchain_received = False,loadState=True,
               networkPartition=False, partitionTimer=60, partitionCounter=1 ):

    self.ID = id
    self.ip = ip
    self.port = port
    self.stateFile = "serverState_" + str(self.ID) + ".txt"
    self.blockchain = []
    self.tempTxns = []
    self.pendingBlocksThatNeedsToBeAddedinBlockchain = [] # I will store out of order blocks in this list.

    self.message = None
    self.BallotNum = (0,0,0)       # leader will use this value, for phase-1 messages
    self.AcceptNum = (0,0,0)       # highest proposal value accepted
    self.AcceptVal = None      # corresponding value

    self.otherServers = otherServers
    self.majorityCount = (len(self.otherServers) // 2) + 1
    self.networkPartition = networkPartition
    self.togglePartitionAfterStart = networkPartition

    self.toggleTimer = partitionTimer # change this timer to play around
    self.toggleTimerCount = partitionCounter # must be odd number

    self.partionedServers = {}
    if ( self.ID in [1,2,3] ):
      self.partionedServers = {k: self.otherServers[k] for k in list(self.otherServers.keys())[:2]}
    elif ( self.ID in [4,5] ):
      self.partionedServers = {k: self.otherServers[k] for k in list(self.otherServers.keys())[-1]}

    self.currentBlockNumber = 0  # blocks that are already agreed upon. I will start new block with this number
    self.currentTerm = 0         # block number that I am interested in at present
    self.blockInitiatedByMyself = {} # dictionary that stores the blocks already started by myself

    self.Acceptor = Acceptor() # I am always an acceptor
    self.Leader = None # I will create a leader obect and then destroy it once completed
    self.LeaderElectionRetries = 3
    self.TrackLeaderProgress = 0


    self.listenToBlockchainChannel()
    self.blockchain_received = blockchain_received
    self.loadState = loadState
    self.saveState = ServerConfig.saveState
    self.getUpdatedBlockChain()
    self.pendingMessagesToBeSent = [] # I will store the messages that I need to send in this queue.
    self.run()

    self.stopLeaderTrying = False

    print("Setup for Server" + str(self.ID) + " done!")
    saveStateThread = threading.Thread(target=self.saveMyState)
    saveStateThread.start()
    self.client_connection = ( client_ip, client_port )

  def loadMyState(self):
    if(os.path.exists(self.stateFile)):
      savedState = None
      pickle_in = open(self.stateFile, "rb")
      savedState = pickle.load(pickle_in)

      if(savedState != None):
        self.blockchain = savedState.blockchain
        self.BallotNum = savedState.ballotNum
        self.tempTxns = savedState.tempTxns
        print("NODE- State of server loaded from file")

  def saveMyState(self):
    while( self.saveState ):
      sleep(ServerConfig.saveStateTimer)
      filename = self.stateFile
      serverState = ServerState(self.blockchain, self.BallotNum, self.tempTxns)
      with open(filename, "wb") as f:
        pickle.dump( serverState, f)
        print("NODE- saving state to disk")

  def getUpdatedBlockChain(self):
    if( self.loadState == True ):
      print("NODE- Loading state of server loaded from file")
      self.loadMyState()
      if( self.blockchain_received == True):
        return

    if( len(self.otherServers.items()) == 0 or self.loadState == True):
      self.blockchain_received = True;

    for key, value in self.otherServers.items():
      value = value.split(",")
      if( ServerUtilities.isOpen(value[0], int(value[1]))):
        message = Send_Your_BlockChain(None, receiver=(value[0], int(value[1])), sender= (( self.ip, self.port+1 )))
        #sleep(5) # need to configure all the sleeps too
        if( ServerUtilities.sendMessage_Thread(message) ):
          break

  def sendMyBlockchain(self, data_received ):
    message = My_BlockChain(self.blockchain, receiver= data_received.sender, sender=data_received.receiver)
    ServerUtilities.sendMessage_Thread( message )

  def sendMyPartialBlockchain(self, data_received ):
    message = My_Partial_BlockChain(self.blockchain, receiver= data_received.sender, sender=data_received.receiver)
    ServerUtilities.sendMessage_Thread( message )

  def getMissingBlockChain(self):
    while(True):
      sleep( ServerConfig.getMissingBlockChainPollingDelay )
      if( len(self.pendingBlocksThatNeedsToBeAddedinBlockchain) > 0 ):
        print("NODE- Need to get the missing blockChain")
        for key, value in self.otherServers.items():
          value = value.split(",")
          if (ServerUtilities.isOpen(value[0], int(value[1]))):
            message = Send_Partial_BlockChain(None, receiver=(value[0], int(value[1])), sender=((self.ip, self.port + 1)))
          #sleep(5)  # need to configure all the sleeps too
            if (ServerUtilities.sendMessage_Thread(message)):
              break
    print("Awesomeness Prevails ... ")

  def togglePartition(self, toggle):
    while(toggle == True and self.toggleTimerCount > 0):
      sleep(self.toggleTimer)
      print("NODE- Is the network partition? : ", str(not self.networkPartition))
      self.networkPartition = not self.networkPartition
      self.toggleTimerCount = self.toggleTimerCount - 1

  def run(self):
    while( self.blockchain_received == False ):
      sleep(1)
    socketThread = threading.Thread(target=self.setupListeningSocket, args=(self.ip, self.port))
    socketThread.start()

    partitionThread = threading.Thread(target=self.togglePartition, args=[self.togglePartitionAfterStart])
    partitionThread.start()

    missingBCThread = threading.Thread(target=self.getMissingBlockChain)
    missingBCThread.start()


  def listenToBlockchainChannel(self):
    bcThread = threading.Thread(target=self.setupListeningSocket, args=(self.ip, self.port+1))
    bcThread.start()

  def startLeaderElection(self):

    if(len(self.tempTxns) < 2):
      return
#    print("NODE - Starting the thread ... ")
    leaderThread = threading.Thread(target=self.startLeaderElectionThread, args=())
    leaderThread.start()

  def startLeaderElectionThread(self):
    # create messages
    # send those messages and listens to the responses
    while( self.LeaderElectionRetries > 0 and len(self.tempTxns) >= 2 ):
      print("Trying to be leader: " + str(self.LeaderElectionRetries ))
      random_delay = ServerConfig.retryLeaderInitiationDelay
      random_delay = random.randrange( random_delay[0], random_delay[1] )
      if( self.LeaderElectionRetries != 3 ):
        sleep( random_delay )
      if( self.Leader != None ):
        print("ProgressMade: "+str(self.Leader.ProgressMade)+" TrackLeaderProgress: "+str(self.TrackLeaderProgress))
        print("BallotNum: " + str(self.Leader.ballotNum_Being_Used))
        # check if progress has been made in retires. If not, reduce the retires number
        if( self.Leader.ProgressMade > self.TrackLeaderProgress ):
          self.TrackLeaderProgress = self.Leader.ProgressMade
          print("Progress made ... ")
          continue
        self.LeaderElectionRetries = self.LeaderElectionRetries - 1

      if( self.LeaderElectionRetries == 0 ):
        self.Leader = None
#        self.currentBlockNumber = self.currentBlockNumber + 1
#        self.BallotNum = (self.BallotNum[0] + 1, self.BallotNum[1], self.BallotNum[2])
        self.LeaderElectionRetries = 3

      if( self.Leader == None and len(self.tempTxns) >= 2 and self.checkValidityOfTransaction(self.tempTxns[0]) and self.checkValidityOfTransaction(self.tempTxns[1]) ):
        prevHash = self.getPreviosBlockHash()
        block = Block( self.currentBlockNumber, prevHash, self.tempTxns[0:2])
        block.findNonceForValidatingTheBlock()
        self.BallotNum = (self.BallotNum[0] + 1, self.ID, self.currentBlockNumber)
        print("LEADER - Started the request for being a leader with ballotNum: " + str(self.BallotNum) )
        self.Leader = Leader((self.ip, self.port), self.BallotNum, block, self.otherServers,self.networkPartition,self.partionedServers)  # I have a leader.object
        self.Leader.handle_Leader_election_Initiation()

  def checkValidityOfTransaction(self, transaction):
    client_sender, client_receiver, transfer_amount = transaction.split(' ')
    available_credit = 100
    lines = ServerUtilities.getTransactionsFromBlockchain( self.blockchain )
    for transaction in lines:
      sender, receiver, amount = transaction.split(' ')
      if (sender == client_sender):
        available_credit = available_credit - int(amount)
      if (receiver == client_sender):
        available_credit = available_credit + int(amount)

    return int(available_credit) >= int(transfer_amount)

  def getPreviosBlockHash(self):
    if( len( self.blockchain ) == 0 ):
      return "NULL"
    else:
      return self.blockchain[-1].hashOfBlock()

  def handle_TransactionReceivedFromClient(self, transaction): # client is not sending its info. We still need to handle
                                                               # server-client interaction
    items = transaction.split(' ')
    if (len(items) == 1):
      query = int(items[0])
      if (query == 2):
        ServerUtilities.replyToClient( self.client_connection, self.blockchain )
        return
      if (query == 3):
        result = ServerUtilities.getBalanceForAll( self.blockchain )
        ServerUtilities.replyToClient( self.client_connection, result )
        return
      if (query == 4):
        ServerUtilities.replyToClient( self.client_connection, self.tempTxns )
        return

    number, client_sender, client_receiver, transfer_amount = transaction.split(' ')
    transaction = client_sender + " " + client_receiver  + " " + transfer_amount
    validity = self.checkValidityOfTransaction( transaction )
    if( validity == False ):
      ServerUtilities.replyToClient( self.client_connection, "INVALID TRANSACTION : " + transaction )
      return

    print("LEADER - Transaction received!")
    print("\t Add transaction received from client in tmpTXns")

    self.tempTxns.append(transaction)
    ServerUtilities.replyToClient( self.client_connection, "TRANSACTION accepted for processing: " + transaction)
    self.startLeaderElection()

  def setupListeningSocket( self, host, port ):
    listeningPort = socket.socket()
    listeningPort.bind(( host, port ))
    listeningPort.listen( 10 )
    while True:
      conn, addr = listeningPort.accept()
      data = conn.recv( 51200 )
      if( not len(data) > 0):
        continue
      data_object = pickle.loads( data )

      if ( isinstance( data_object, Send_Your_BlockChain) ):
        self.sendMyBlockchain(data_object)
      elif ( isinstance( data_object, My_BlockChain) ):
        self.blockchain = data_object.ballotNum
        if( len(self.blockchain) > 0 ):
          self.currentBlockNumber = self.blockchain[-1].currentBlockDepth + 1
        self.blockchain_received = True
      elif ( isinstance( data_object, Send_Partial_BlockChain) ):
        self.sendMyPartialBlockchain(data_object)
      elif ( isinstance( data_object, My_Partial_BlockChain) ):
        received_blockchain = data_object.ballotNum
        if( len(received_blockchain) > len(self.blockchain) ):
          if( received_blockchain[-1].currentBlockDepth == self.pendingBlocksThatNeedsToBeAddedinBlockchain[-1].currentBlockDepth):
            self.pendingBlocksThatNeedsToBeAddedinBlockchain = []
            self.blockchain = received_blockchain
            if (len(self.blockchain) > 0 ):
              self.currentBlockNumber = self.blockchain[-1].currentBlockDepth + 1


      # handled as Leader
      elif (isinstance(data_object, str)):
        self.handle_TransactionReceivedFromClient(data_object)

      # handled as Leader
      elif ( isinstance( data_object, Ack_Phase1 ) ):
        if(self.Leader != None and data_object.ballotNum == self.Leader.ballotNum_Being_Used ):
          sendNextMessage = self.Leader.handle_Ack_Phase1( data_object )

      elif ( isinstance( data_object, Accept_AcceptorToLeader_Phase2 ) ):
        if( self.Leader != None and data_object.ballotNum == self.Leader.ballotNum_Being_Used ):
          decisionMade = self.Leader.handle_Accept_AcceptorToLeader_Phase2(data_object)
          if ( decisionMade ):
            if (self.Leader.block.txns[0] == self.tempTxns[0] and self.Leader.block.txns[1] == self.tempTxns[1]):
              print("\t Removing two transactions from")
              self.tempTxns = self.tempTxns[2:]
              ServerUtilities.replyToClient( self.client_connection, "TRANSACTION recorded in blockchain: " + self.Leader.block.txns[0] )
              ServerUtilities.replyToClient( self.client_connection, "TRANSACTION recorded in blockchain: " + self.Leader.block.txns[1] )
      # handled as ACCEPTOR
      elif (isinstance(data_object, Prepare_Phase1)):
        print("ACCEPTOR - Received Prepare message [PHASE-1] with ballotNUm: " + str(data_object.ballotNum))
        print("\tMy ballotNum is " + str(self.BallotNum) )
        if (Acceptor.compareBallot(data_object.ballotNum, self.BallotNum) != -1):
          message = Ack_Phase1(data_object.ballotNum, self.AcceptNum, self.AcceptVal, data_object.sender,
                               data_object.receiver)
          self.BallotNum = data_object.ballotNum
          ServerUtilities.sendMessage_Thread( message )

      elif (isinstance(data_object, Accept_LeaderToAcceptor_Phase2)):
        print("ACCEPTOR - Received Accept message [PHASE-2] with ballotNum: " + str(data_object.ballotNum))
        if (Acceptor.compareBallot(data_object.ballotNum, self.BallotNum) != -1):
          self.AcceptNum = data_object.ballotNum
          self.AcceptVal = data_object.acceptVal

          #potential bug
          #message = Accept_AcceptorToLeader_Phase2(message.ballotNum, data_object.acceptVal, data_object.sender, data_object.receiver)
          message = Accept_AcceptorToLeader_Phase2(data_object.ballotNum, data_object.acceptVal, data_object.sender, data_object.receiver)
          ServerUtilities.sendMessage_Thread( message )


      elif (isinstance(data_object, Decision_Phase2)):
        print("ACCEPTOR - Received Decision message [PHASE-2] with ballotNum: " + str(data_object.ballotNum))
        self.AcceptVal = data_object.acceptVal
        self.AcceptNum = data_object.ballotNum
        if( len(self.blockchain) == 0 and data_object.acceptVal and data_object.acceptVal.currentBlockDepth == 0):
          self.blockchain.append(data_object.acceptVal)
          self.currentBlockNumber = data_object.acceptVal.currentBlockDepth + 1
        elif(  data_object.acceptVal.currentBlockDepth == self.currentBlockNumber ):
          self.blockchain.append(data_object.acceptVal)
          self.currentBlockNumber = data_object.acceptVal.currentBlockDepth + 1
        elif( data_object.acceptVal.currentBlockDepth > self.currentBlockNumber  ):
          self.pendingBlocksThatNeedsToBeAddedinBlockchain.append(data_object.acceptVal)
        # destroy the leader and then start the new one.
        if( self.Leader != None and data_object.sender == data_object.receiver ):# this decision was reached by myself
          print("\t Leader destroyed")
          self.TrackLeaderProgress = 0
          self.LeaderElectionRetries = 3
          self.Leader = None
        print("\t Decision message processed")
        print("-------------------------------")

      conn.close()

  def addToBlockchain(self, txns):
    block = Block(self.currentTerm, txns)
    block.hash_block()
    if len(self.blockchain) == 0:
      block.hash_prev_block(None)
    else:
      block.hash_prev_block(self.blockchain[len(self.blockchain)-1])
    self.lastLogIndex = len(self.blockchain) + 1
    self.blockchain.append(block)

  def sendMoneyUpdateToClients(self, txns):
    clientPorts = 8081
    for clientId in clientPorts:
      for trans in txns:
        if trans.split(' ')[0].lower() == clientId or trans.split(' ')[1].lower() == clientId:
          try:
            s = socket.socket()
            s.connect((self.host, clientPorts[clientId]))
            s.send(pickle.dumps(trans))
            s.close()
          except:
            print("Client" + str(clientId).upper() + " is down!")
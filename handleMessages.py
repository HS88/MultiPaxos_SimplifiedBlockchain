from paxosMessage import Prepare_Phase1, Ack_Phase1, Accept_LeaderToAcceptor_Phase2, Accept_AcceptorToLeader_Phase2, Decision_Phase2
import socket
import pickle
from Configuration import *
import random
from time import sleep

class Acceptor:

  @staticmethod
  def compareBallot( bal1, bal2 ): #receivedBallotNum, myBallotNum
    result = 0
    print("\treceivedBallot: ", str(bal1))
    print("\tmydBallot: ", str(bal2))

    if(ServerConfig.networkPartioned == False):
      if( bal2[0] == bal2[1] and bal2[1]== bal2[2] and bal2[2]== 0 and bal1[0] > 0):
        return 1

      if( bal1[0] == bal2[0] and bal1[1] == bal2[1] and bal1[2] == bal2[2] ):
        result = 0
      elif ( bal1[0] > bal2[0] or ( bal1[0] == bal2[0] and bal1[1] > bal2[1] ) or (  bal1[0] == bal2[0] and bal1[1] == bal2[1] and bal1[2] > bal2[2])):
        result = 1
      elif (bal1[2] < bal2[2] or (
                bal1[2] == bal2[2] and not (bal1[0] == bal2[0] and bal1[1] == bal2[1] and bal1[2] == bal2[2]))):
          return -1
      else:
        result = -1
      print("NODE- Ballot comparison result: ", str(result))
      print("\treceivedBallotNum < myBallotNum: 1\n\treceivedBallotNum == myBallotNum: 0\n\treceivedBallotNum > myBallotNum: -1")
      return result

    else:
      if (bal2[0] == bal2[1] and bal2[1] == bal2[2] and bal2[2] == 0 and bal1[0] > 0):
        return 1

      if (bal1[2] < bal2[2] or (
              bal1[2] == bal2[2] and not (bal1[0] == bal2[0] and bal1[1] == bal2[1] and bal1[2] == bal2[2]))):
        return -1
      if (bal1[0] == bal2[0] and bal1[1] == bal2[1] and bal1[2] == bal2[2]):
        result = 0
      elif (bal1[0] > bal2[0] or (bal1[0] == bal2[0] and bal1[1] > bal2[1]) or (
              bal1[0] == bal2[0] and bal1[1] == bal2[1] and bal1[2] > bal2[2])):
        result = 1

      else:
        result = -1
      print("NODE- Ballot comparison result: ", str(result))
      print(
        "\treceivedBallotNum < myBallotNum: 1\n\treceivedBallotNum == myBallotNum: 0\n\treceivedBallotNum > myBallotNum: -1")
      return result


  def sendMessage(self, message):
    delay = ServerConfig.serverToServerDelay
    delay = random.randrange( delay[0], delay[1] )
    sleep(delay)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ( message.receiver )

    try:
      sock.connect(server_address)
      sock.sendall(pickle.dumps(message))
    except:
      print("Exception occurred while sending data to server")
      return "Exception occurred while sending data to server"
    finally:
      try:
        sock.shutdown(socket.SHUT_RDWR)
      finally:
        sock.close()


  def handle_Prepare_Phase1(self, BallotNum, AcceptNum, AcceptVal, message):
    print("ACCEPTOR - Received Prepare message [PHASE-1]")
    if( Acceptor.compareBallot( message.ballotNum, BallotNum ) == 0):
      print("\t sending ack back to leader")
      message = Ack_Phase1(message.ballotNum, AcceptNum, AcceptVal, message.sender ,message.receiver)
      self.sendMessage( message )
    return

  def handle_Accept_LeaderToAcceptor_Phase2(self):
    print("3-Acceptor received Accept message [PHASE-2]")

  def handle_Decision_Phase2(self, messag):
    print( "5-Acceptor received Decision message [PHASE-2]" )

class Leader:
  def __init__(self, sender, ballotNum, block, otherServers, partition=False, partitionServers={}):
    self.sender = sender
    self.ballotNum_Being_Used = ballotNum
    self.block    = block                  # this is the block that I want all to accept [Initial Value]
    self.otherServers  = otherServers
    self.majorityCount = (len(self.otherServers)//2) + 1
    self.ackReceived    = set()
    self.acceptReceived = set()
    self.ackReceivedMajority = False
    self.acceptReceivedMajority = False
    self.waitTimer = None
    self.ProgressMade = 1
    self.partitionServers = partitionServers
    self.partition = partition

  def sendMessage(self, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ( message.receiver )
    try:
      sock.connect(server_address)
      sock.sendall(pickle.dumps(message))
    except:
      print("Exception occurred while sending data to server")
      return "Exception occurred while sending data to server"
    finally:
      try:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
      except:
        print()

  def handle_Ack_Phase1(self, message ):
    print("LEADER - Received Ack message [PHASE-2 initiation] with ballotNum: " + str(message.ballotNum))
    # process the messages of this type
    sendNextMessage = False
    # need one check. It is the ack for the same block that I am trying at present
    if( message.ballotNum != self.ballotNum_Being_Used ):
      print("\t Ack received, but does not match the ballotNUm being used at present")
      return

    self.ackReceived.add( message )
    self.ProgressMade = self.ProgressMade + 1

    if( len(self.ackReceived) >= self.majorityCount and self.ackReceivedMajority == False ):
      print("\t Majority acks received in phase-2 initiation")
      self.ackReceivedMajority = True
      sendNextMessage = True
      valReceived = set()
      highestBal = (0, 0, 0)
      for message in self.ackReceived:
        if (message.acceptVal == None or message.ballotNum[2] >= self.ballotNum_Being_Used[2]):
          continue
        else:
          valReceived.add(message)
      for message in valReceived:
        if (Acceptor.compareBallot( highestBal, message.ballotNum) == -1):
          self.block = message.acceptVal
          print("\t AcceptVal with highest ballotNum is selected as a value")

      contactServers = self.otherServers
      if(self.partition==True):
        contactServers = self.partitionServers

      for key, value in contactServers.items():
        value = value.split(",")
        message = Accept_LeaderToAcceptor_Phase2(self.ballotNum_Being_Used, self.block, receiver=(value[0], int(value[1])), sender=self.sender)
        self.sendMessage(message)
      message = Accept_LeaderToAcceptor_Phase2(self.ballotNum_Being_Used, self.block, receiver=self.sender, sender=self.sender )
      self.sendMessage(message)

    return sendNextMessage

  def handle_Accept_AcceptorToLeader_Phase2(self, message):
    print("LEADER - Received Accept message [PHASE-2] with ballotNum: " + str(message.ballotNum))
    if ( message.ballotNum == self.ballotNum_Being_Used ):
      self.acceptReceived.add(message)
      self.ProgressMade = self.ProgressMade + 1

    sendMessage = False

    if (len(self.acceptReceived) >= self.majorityCount and self.acceptReceivedMajority == False):
      print("\t Majority accept received [PHASE-2]")
      self.acceptReceivedMajority = True
      sendMessage = True

      contactServers = self.otherServers
      if(self.partition==True):
        contactServers = self.partitionServers


      for key, value in contactServers.items():
        value = value.split(",")
        message = Decision_Phase2( message.ballotNum, message.acceptVal, receiver=(value[0], int(value[1])), sender=self.sender )
        self.sendMessage(message)
      message = Decision_Phase2( message.ballotNum, message.acceptVal, receiver=self.sender, sender=self.sender )
      self.sendMessage(message)
    return sendMessage

  def handle_Leader_election_Initiation(self):

    contactServers = self.otherServers
    if (self.partition == True):
      contactServers = self.partitionServers

    for key, value in contactServers.items():
      value = value.split(",")
      message = Prepare_Phase1( self.ballotNum_Being_Used, receiver=( value[0], int(value[1]) ), sender=self.sender )
      self.sendMessage(message)
    message = Prepare_Phase1(self.ballotNum_Being_Used, receiver=self.sender, sender=self.sender )
    self.sendMessage(message)
class Message:
    messageType = {
    "Prepare_Phase1" : 0,
    "Ack_Phase1" : 1,
    "Accept_LeaderToAcceptor_Phase2" : 2,
    "Accept_AcceptorToLeader_Phase2": 3,
    "Decision_Phase2":4
    }

    def __init__(self, ballotNum, acceptNum = None, acceptVal = None, receiver=None, sender=None):
        self.sender = sender        #(ip,port) of sending server
        self.receiver = receiver    #(ip,port) of receiving server
        self.ballotNum = ballotNum
        self.acceptNum = acceptNum
        self.acceptVal = acceptVal


    def __eq__(self, other):
        if not isinstance( other, Message ):
            return NotImplemented

        return self.sender == other.sender and self.receiver == other.receiver and self.ballotNum == other.ballotNum and \
               self.acceptNum == other.acceptNum and self.acceptVal == other.acceptVal

    def __hash__(self):
        return hash(( self.sender, self.receiver, self.ballotNum, self.acceptNum, self.acceptVal ))

class Send_Partial_BlockChain(Message):
    def __init__(self, ballotNum, receiver, sender):
        Message.__init__(self, ballotNum, receiver=receiver, sender=sender) # this ballotnum can be the starting index from which i need the blockchain

class My_Partial_BlockChain(Message):
    def __init__(self, blockChain, receiver, sender):
        Message.__init__(self, blockChain, receiver=receiver, sender=sender)

class Send_Your_BlockChain(Message):
    def __init__(self, ballotNum, receiver, sender):
        Message.__init__(self, ballotNum, receiver=receiver, sender=sender)

class My_BlockChain(Message):
    def __init__(self, blockChain, receiver, sender):
        Message.__init__(self, blockChain, receiver=receiver, sender=sender)

class Prepare_Phase1(Message):
    def __init__(self, ballotNum, receiver, sender):
        Message.__init__(self, ballotNum, receiver=receiver, sender=sender)

class Ack_Phase1(Message):
    def __init__(self, ballotNum, acceptNum, acceptVal, receiver, sender):

        Message.__init__(self,  ballotNum, acceptNum, acceptVal, receiver, sender)

class Accept_LeaderToAcceptor_Phase2(Message):
    def __init__(self, ballotNum, acceptVal, receiver, sender):
        Message.__init__(self, ballotNum, acceptVal=acceptVal, receiver=receiver, sender=sender)

class Accept_AcceptorToLeader_Phase2(Message):
    def __init__(self, ballotNum, myVal, receiver,sender):
        Message.__init__(self, ballotNum, acceptVal=myVal,receiver=receiver, sender=sender)

class Decision_Phase2(Message):
    def __init__(self, ballotNum, myVal, receiver, sender):
        Message.__init__(self, ballotNum, acceptVal=myVal, receiver=receiver, sender=sender)
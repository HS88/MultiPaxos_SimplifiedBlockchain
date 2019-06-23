import queue as Q
import socket, pickle
import select, threading
from Block import Block
import random
from time import sleep
from Configuration import *

class Client:
    def __init__(self, id, ip, port, server_ip, server_port, maxConnections):
        self.ID = id
        self.ip = ip
        self.port = port
        self.server_connection = (server_ip, server_port)
        self.pendingTransactions = Q.Queue()
        self.CONNECTION_LIST = []
        self.maxConnections = maxConnections
        self.message_from_server=""

        self.CONNECTION_LIST = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))  # I am listening to this port for all messages
        self.server_socket.listen(10)
        print("Client ID: ", self.ID)
        print("Client listening at", self.ip, self.port)
        self.CONNECTION_LIST.append(self.server_socket)

        return

    def validTransaction(self, transaction):
        try:
            sender, receiver, amount = transaction.split(" ")
            result = int(amount) > 0 and sender==self.ID
        except:
            result = False
        finally:
            return result

    def composeMessage(self, transaction):
        message = "{},{};INITIATE;NA;{},{};{}".format(self.server_connection[0],self.server_connection[1], self.ip, self.port, transaction)
        return message

    def sendMessageToServer(self, transaction):
        print("A thread will send the data to the server")
        print("Start the thread that listens to the server response")

        delay = ServerConfig.clientToServerDelay
        delay = random.randrange(delay[0], delay[1])
        sleep(delay)
        Message = self.composeMessage( transaction )
        sock_send_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ( self.server_connection )
        sock_send_to_server.connect(server_address)

        self.message_from_server = ""
        try:
            sock_send_to_server.sendall(pickle.dumps( transaction ))
        except:
            print("Exception occurred while sending data to server")
            return "Exception occurred while sending data to server"
        finally:
            sock_send_to_server.shutdown(socket.SHUT_RDWR)
            sock_send_to_server.close()
            waitReply = False
            while (waitReply == True):
                read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])
                for sock in read_sockets:
                    if sock == self.server_socket:
                        sockfd, addr = self.server_socket.accept()
                        self.CONNECTION_LIST.append(sockfd)
                    else:
                        try:
                            data = sock.recv(4096)
                            addr = sock.getsockname()
                        except:
                            print("Client (%s, %s) is disconnected" % addr)
                            sock.close()
                            self.CONNECTION_LIST.remove(sock)
                            continue
                        if data:
                            self.message_from_server = data.decode("utf-8")
                            self.CONNECTION_LIST.remove(sock)
                            waitReply = False
                            break
                sock.shutdown(socket.SHUT_RDWR)
        print("Client closing socket after response from server")
        return self.message_from_server

    def listenToServerResponse(self):
        print("A thread will start listening to the server response")
        print("Waiting for server response")
        while ( True ):
            read_sockets, write_sockets, error_sockets = select.select(self.CONNECTION_LIST, [], [])
            for sock in read_sockets:
                if sock == self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    self.CONNECTION_LIST.append(sockfd)
                else:
                    try:
                        data = sock.recv(4096)
                        addr = sock.getsockname()
                        message_received = pickle.loads(data)
                    except:
                        print("Client (%s, %s) is disconnected" % addr)
                        sock.close()
                        self.CONNECTION_LIST.remove(sock)
                        continue
                    if data:
                        if ( isinstance(message_received, list) ):
                            result = ""
                            if( len( message_received ) > 0 and isinstance(message_received[0], Block) ):
                                for block in message_received:
                                    result = result + str(block) + "-----------------\n"
                            else:
                                result = str(message_received)
                            self.message_from_server = "\nSERVER RESPONSE: " + str(result)
                        else:
                            self.message_from_server = "\nSERVER RESPONSE: " + str(message_received)
                        self.CONNECTION_LIST.remove(sock)
                        print( self.message_from_server )

    def startClient(self):
        socketThread = threading.Thread(target=self.listenToServerResponse)
        socketThread.start()

        while (True):
            print( "Client ID: " + str(self.ID) +
                   "\nWhat query you want to make?\
                   \nEnter the number\
                   \n1-moneyTransfer\
                   \n2-printBlockchain:\
                   \n3-printBalance:\
                   \n4-printSet\n")
            choice = int(input())
            if(choice == 1):
                if( self.pendingTransactions.empty() == False ):
                    continue
                text = input( "Enter Transaction: \n" )
                if ( self.validTransaction(text)):
                    print("Send transaction to server... with connection details as: ", self.server_connection )
                    message_from_server = self.sendMessageToServer(str(choice) + " " + text)
                    print(message_from_server)
                else:
                    print("Enter transaction in valid format ...")
            elif( choice == 2):
                message_from_server = self.sendMessageToServer(str(choice))
                print(message_from_server)

            elif(choice == 3):
                message_from_server = self.sendMessageToServer(str(choice))
                print(message_from_server)
            elif(choice == 4):
                message_from_server = self.sendMessageToServer(str(choice))
                print(message_from_server)
            else:
                print("Enter valid choice please")
        exit()
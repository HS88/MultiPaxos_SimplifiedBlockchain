from random import randint, choice
import hashlib as hasher
import string

class Block:
    def __init__(self, currentBlockDepth, hashOfPrevBlock ,txns):
        self.currentBlockDepth = currentBlockDepth
        self.hashOfPrevBlock = hashOfPrevBlock
        self.nonce = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(8))
        self.txns = txns

    def findNonceForValidatingTheBlock(self):
        while True:
            self.nonce = ''.join(choice(string.ascii_uppercase + string.digits) for _ in range(8))
            hashTxns = hasher.sha256()
            hashTxns.update(
                (str(self.txns[0]) + str(self.txns[1]) + str(self.nonce)).encode('utf-8')
            )
            hashTxnsHex = hashTxns.hexdigest()
            if ( hashTxnsHex[len( hashTxnsHex)-1:] in ["0", "1"]):
                break

    # this hash of block will be stored in the next block
    def hashOfBlock(self):
        hashPrev = hasher.sha256()
        hashPrev.update(
            (
                    str(self.currentBlockDepth-1)+
                    str(self.hashOfPrevBlock) +
                    str(self.nonce) +
                    str(self.txns[0]) +
                    str(self.txns[1])
            ).encode('utf-8')
        )
        hashOfBlock = hashPrev.hexdigest()
        return hashOfBlock

    def __str__(self):
#        printBlock(self)
        result = "\n"
        result = result + "\tCurrent block depth: " + str(self.currentBlockDepth) + "\n"
        result = result + "\t\tHash of prev block: " + str(self.hashOfPrevBlock) + "\n"
        result = result + "\tNonce: " + str(self.nonce) + "\n"
        result = result + "\tTransactions: " + "\n"
        result = result + "\t\tTransaction 1: " + str(self.txns[0]) + "\n"
        result = result + "\t\tTransaction 2: " + str(self.txns[1]) + "\n"


        return result

def printBlock(block):
    print("\tCurrent block depth: " + str(block.currentBlockDepth))
    print("\t\tHash of prev block: " + str(block.hashOfPrevBlock))
    print("\tNonce: " + str(block.nonce))
    print("\tTransactions: ")
    print("\t\tTransaction 1: " + str(block.txns[0]))
    print("\t\tTransaction 2: " + str(block.txns[1]))

if __name__ == '__main__':
    txns1 = ["A B 5", "B C 10"]
    txns2 = ["B A 10", "B C 10"]
    txns3 = ["A C 10", "C A 20"]

    blockchain = []

    print("\nBlock 1")
    block1 = Block(1, "NULL", txns1)
    block1.findNonceForValidatingTheBlock()

    printBlock(block1)
    blockchain.append(block1)

    print("\nBlock 2")
    prevHash = block1.hashOfBlock()
    block2 = Block(2, prevHash, txns2)
    block2.findNonceForValidatingTheBlock()

    printBlock(block2)
    blockchain.append(block2)

    print("\nBlock 3")
    prevHash = block2.hashOfBlock()
    block3 = Block(3, prevHash, txns3)
    block3.findNonceForValidatingTheBlock()
    printBlock(block3)
    blockchain.append(block3)

    print("\nBlockchain built!\n")
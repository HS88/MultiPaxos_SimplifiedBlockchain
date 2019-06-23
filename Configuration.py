class ServerConfig:
    server_list={1:'127.0.0.1,8080', 2:'127.0.0.1,8090', 3:'127.0.0.1,8100', 4:'127.0.0.1,8110', 5:'127.0.0.1,8130'}
    other_server_list = {
        1: {'B': "127.0.0.1,8090", 'C': "127.0.0.1,8100", 'D': "127.0.0.1,8110", 'E': "127.0.0.1,8130"},
        2: {'A': "127.0.0.1,8080", 'C': "127.0.0.1,8100", 'D': "127.0.0.1,8110", 'E': "127.0.0.1,8130"},
        3: {'A': "127.0.0.1,8080", 'B': "127.0.0.1,8090", 'D': "127.0.0.1,8110", 'E': "127.0.0.1,8130"},
        4: {'A': "127.0.0.1,8080", 'B': "127.0.0.1,8090", 'C': "127.0.0.1,8100", 'E': "127.0.0.1,8130"},
        5: {'A': "127.0.0.1,8080", 'B': "127.0.0.1,8090", 'C': "127.0.0.1,8100", 'D': "127.0.0.1,8110"}
    }
    client_list = {
        1: '127.0.0.1,8082',
        2: '127.0.0.1,8092',
        3: '127.0.0.1,8102',
        4: '127.0.0.1,8112',
        5: '127.0.0.1,8132'
    }
    networkPartioned = False
    partitionTimer = 75
    partitionTimerCount = 3

    clientToServerDelay = (1,3)
    serverToServerDelay = (1,5)
    serverToServerBackChannelDelay=(1,2)
    getMissingBlockChainPollingDelay = 10
    retryLeaderInitiationDelay = (5,10)
    saveStateTimer = 60
    saveState = True
    loadState = True

class ClientConfig:

    server_list = {
        1: '127.0.0.1,8080',
        2: '127.0.0.1,8090',
        3: '127.0.0.1,8100',
        4: '127.0.0.1,8110',
        5: '127.0.0.1,8130'
    }

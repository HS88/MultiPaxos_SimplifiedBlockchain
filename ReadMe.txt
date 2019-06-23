Configuration.py:
    This file contains the details of servers' and clients' ip addresses and port number.
    This file contains the details of various delay timers that are used in protocol.

Client_Main.py:
    This file contains the logic of client class.

clientProcess_xx.py:
    These files contain the logic of client instance. To run the client, use
        python clientProcess_<id>.py <id>, where id can be [1,2,3,4,5]

Server_Main.py:
    This file contains the logic of server class.

Server_xx.py:
    These files creates an instance of server and run the process using command:
        python Server_<id>.py <id> <get_blockchain_from_other_servers>
            where id can be [1,2,3,4,5]
            and get_blockchain_from_other_servers can be [1 for yes, 2 for no]

        example:
            first server run without requesting blockchain from others as:
                python Server_1.py 1 2

            other servers run as
                python Server_3.py 3 1

    To run server such that it recovers from other servers while booting:
        python Server_1,.py 1 1
import socket
import select
import time
import sys

# CONFIG
HOST = "irc.freenode.net"
PORT = 6667
NICK = "albot"
IDENT = "albot"
REALNAME = "albot"
RECONNECT_SLEEP = 5

# STATES
INIT_OK = 0
CONNECTION_PROBLEM = 1

# CONNECT
while True:
    sys.stderr.write('connecting..')
    s = socket.socket()
    s.connect((HOST, PORT))
    sys.stderr.write(' ok\n')
    #s.send("NICK %s\r\n" % NICK)
    #s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
    
    state = INIT_OK
    msg = ""
    
    while state != CONNECTION_PROBLEM:
        try:
            ready_read, ready_write, ready_err = select.select([s], [s], [s])

        except socket.error:
            sys.stderr.write('error: connection error. disconnecting..')
            s.shutdown(2)
            s.close()
            sys.stderr.write(' ok\n')
            state = CONNECTION_PROBLEM
            break

        if len(ready_read) > 0:
            sys.stderr.write('read_ready:'+str(len(ready_read)))
            tmp = s.recv(1024)
            sys.stdout.write(tmp)

        if len(ready_write) > 0:
            pass

        #temp = string.split(readbuffer, "\n")
        #readbuffer = temp.pop( )
    
        #for line in temp:
        #    line = string.rstrip(line)
        #    line = string.split(line)
    
        #    if(line[0] == "PING"):
        #        s.send("PONG %s\r\n" % line[1])

    # dead connection, sleep first before retry
    time.sleep(RECONNECT_SLEEP)

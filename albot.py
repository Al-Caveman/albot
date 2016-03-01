import socket
import select
import time
import sys
from getpass import getpass

# HI
sys.stderr.write('hi - welcome to albot; the legandary irc client\n')
sys.stderr.write('that is way better than your mom.\n\n')
sys.stderr.write('licensed under GPLv3, which is described here:\n')
sys.stderr.write('  https://www.gnu.org/licenses/gpl-3.0.en.html\n\n')


# CONFIG
HOST = "irc.freenode.net"
PORT = 6667
NICK = "albot"
IDENT = "albot"
REALNAME = "albot"
RECONNECT_SLEEP = 5
PASSWORD = getpass('gimme yer password: ')

# STATES
INIT_OK = 0
CONNECTION_PROBLEM = 1
COMMAND = 2
PARAMS = 3
CR = 4

# DISCONNECT
def disco(s):
    sys.stderr.write('error: connection error. disconnecting..')
    s.close()
    state = CONNECTION_PROBLEM
    sys.stderr.write(' ok\n')

def ircsend(s, msg):
    sys.stderr.write('>>>>>>>:' + msg)
    s.send(msg)

# CONNECT
while True:
    sys.stderr.write('connecting..')
    s = socket.socket()
    s.connect((HOST, PORT))
    sys.stderr.write(' ok\n')
    ircsend(s, 'PASS ' + PASSWORD + '\r\n')
    ircsend(s, 'NICK ' + NICK + '\r\n')
    ircsend(s, 'USER %s %s bla :%s\r\n' % (IDENT, HOST, REALNAME))
    
    state = INIT_OK
    irc_command = ''
    irc_params = ''
    
    while state != CONNECTION_PROBLEM:
        # wait until connection is ready
        try:
            ready_read, ready_write, ready_err = select.select([s], [s], [s])
        except select.error:
            break

        # read ready
        if len(ready_read) > 0:
            tmp = s.recv(1024)
            sys.stderr.write('***|'+tmp+'|***\n')
            if (len(tmp) == 0):
                disco(s)
                break
            else:
                for c in tmp:
                    if state == INIT_OK: # start of a new message
                        if c == ' ':
                            state = COMMAND

                    elif state == COMMAND: # reading command
                        if c == ' ':
                            state = PARAMS
                        else:
                            irc_command += c

                    elif state == PARAMS: # reading params
                        if c == '\r':
                            sys.stderr.write('command:' + irc_command + '\n')
                            sys.stderr.write('  params:' + irc_params + '\n')
                            state = CR
                        else:
                            irc_params += c

                    elif state == CR: # anticipating params end signal
                        if c == '\n':
                            irc_command = ''
                            irc_params = ''
                            state = INIT_OK

        # write ready
        if len(ready_write) > 0:
            pass

    # dead connection, sleep first before retry
    sys.stderr.write('reconnecting in '+str(RECONNECT_SLEEP)+' seconds..')
    time.sleep(RECONNECT_SLEEP)

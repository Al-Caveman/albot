# albot - the legendary irc bot that is way better than your mom.
# Copyright (C) 2016 caveman <toraboracaveman@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
import select
import time
import sys
import re
from getpass import getpass
import random

# HI
sys.stderr.write('hi - welcome to albot; the legandary irc bot\n')
sys.stderr.write('that is way better than your mom.\n\n')

# CONFIG
VERBOSE = True
HOST = "irc.freenode.net"
PORT = 6667
NICK = "albot"
IDENT = "albot"
REALNAME = "albot"
RECONNECT_SLEEP = 5
PASSWORD = getpass('gimme yer password: ')
CHANNELS = ['##caveman', '#gentoo-chat-exile']

# STATES
INIT_OK = 0
CONNECTION_PROBLEM = 1
COMMAND = 2
PARAMS = 3
CR = 4
INIT_MAYBE = 5

# DISCONNECT
def disco(s):
    sys.stderr.write('error: connection error. disconnecting..')
    s.close()
    state = CONNECTION_PROBLEM
    sys.stderr.write(' ok\n')

# SEND TO IRC SERVER
def ircsend(s, msg):
    if VERBOSE:
        sys.stderr.write('>>>>>>:' + msg)
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
    irc_prefix = ''
    irc_command = ''
    irc_params = ''
    
    while state != CONNECTION_PROBLEM:
        # wait until connection is ready
        try:
            ready_read, ready_write, ready_err = select.select([s], [ ], [s])
        except select.error:
            # not sure what to add here. this part needs to be revised.
            break

        # read ready
        if len(ready_read) > 0:
            tmp = s.recv(1024)
            if (len(tmp) == 0):
                disco(s)
                break
            else:
                for c in tmp:
                    if state == INIT_OK: # start of a new message
                        if c == ' ':
                            state = COMMAND
                        else:
                            irc_prefix += c

                    elif state == COMMAND: # reading command
                        if c == ' ':
                            state = PARAMS
                        else:
                            irc_command += c

                    elif state == PARAMS: # reading params
                        if c == '\r':
                            if VERBOSE:
                                sys.stderr.write('prefix:' + irc_prefix + '\n')
                                sys.stderr.write('  command:' + irc_command + '\n')
                                sys.stderr.write('  params :' + irc_params + '\n')

                            #
                            # bot stuff start here
                            #
                            # do pings
                            if irc_command == 'PING':
                                ircsend(s, 'PONG ' + irc_params + '\r\n')

                            # join channels only if authenticated and hidden
                            if irc_command == '396':
                                for channel in CHANNELS:
                                    ircsend(s, 'JOIN ' + channel + '\r\n')

                            if irc_command == 'PRIVMSG':
                                # parse message
                                irc_prefix_nick = irc_prefix[0:irc_prefix.find('!')]
                                irc_params_channel = irc_params[0:irc_params.find(' ')]
                                irc_params_msg = irc_params[irc_params.find(' ')+2:]

                                # did anyone mention albot?
                                if re.search('(\W|^)' + NICK + '(\W|$)', irc_params_msg):
                                    albot_mentioned = True
                                else:
                                    albot_mentioned = False

                                # respond
                                if albot_mentioned:
                                    responses = {1: 'a dab will do ya!',
                                        2: 'caveman perfected me with the beauty of simplicity. check my guts here: https://github.com/Al-Caveman/albot',
                                        3: 'am still incomplete dude.. awaiting master caveman to bless me one day',
                                        4: 'you talkin to me?',
                                        5: 'some say my master caveman is stoopid but master says these are jelly bastards',
                                        6: 'check me am naked here https://github.com/Al-Caveman/albot',
                                        7: 'a dab may do ya! lol',
                                        8: 'lord caveman is wise he answers every question i can think of',
                                        9: 'all irc bots suck (master says), until master decided to make me',
                                        10: 'some say am the beauty of simplicity'}

                                    ircsend(s, 'PRIVMSG '
                                        + irc_params_channel
                                        + ' :'+responses[random.randint(1,len(responses))]+'\r\n')

                            #
                            # bot stuff end here
                            #

                            state = CR
                        else:
                            irc_params += c

                    elif state == CR: # anticipating params end signal
                        if c == '\n':
                            irc_prefix = ''
                            irc_command = ''
                            irc_params = ''
                            state = INIT_MAYBE

                    elif state == INIT_MAYBE: # anticipating non-prefixed commands
                        if c == ':':
                            state = INIT_OK
                        else:
                            irc_command += c
                            state = COMMAND

    # dead connection, sleep first before retry
    sys.stderr.write('reconnecting in ' + str(RECONNECT_SLEEP) + ' seconds..')
    time.sleep(RECONNECT_SLEEP)

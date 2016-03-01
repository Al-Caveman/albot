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
from getpass import getpass
import re
import hashlib
import os

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
CHANNELS = ['##caveman']

# STORAGE OBJECT NAMES
STORAGE_ROOT = os.path.splitext(os.path.basename(__file__))[0]
KARMA = 'karma'

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

# GET OBJECT PATH
def getobjpath(t, o):
    # sanitify object name
    o_sane = hashlib.md5(bytes(o)).hexdigest()
    n = 2
    return STORAGE_ROOT + '/' + t + '/' + '/'.join([o_sane[i:i+n] for i in range(0,len(o_sane),n)])

# GET OBJECT VALUE
def getobj(t, o):
    o_path = getobjpath(t, o)
    try:
        with open(o_path, 'r') as f:
            v = f.read()
    except:
        v = None
    return v

# SET OBJECT VALUE
def setobj(t, o, v):
    o_path = getobjpath(t, o)
    try:
        os.makedirs(os.path.dirname(o_path))
    except:
        pass

    try:
        with open(o_path, 'w') as f:
            f.write(bytes(v))
    except:
        sys.stderr.write('error: failed to save object "'+o_path+'".\n')

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

                                # did anyone address albot?
                                if irc_params_msg.find(NICK) == 0:
                                    ircsend(s, 'PRIVMSG ' + irc_params_channel
                                    + ' :' + irc_prefix_nick + ', called me?\r\n')

                                # simple karma bot
                                # increment karma
                                if re.search('^[\S]+\+\++', irc_params_msg):
                                    karma_subject = re.search('^[\S]+\+\+', irc_params_msg).group()[0:-2]
                                    karma_subject_score = getobj(KARMA, karma_subject)
                                    if karma_subject_score == None:
                                        karma_subject_score = 0
                                    else:
                                        karma_subject_score = int(karma_subject_score)
                                    setobj(KARMA, karma_subject, karma_subject_score+1)

                                # decrement karma
                                if re.search('^[\S]+\-\-+', irc_params_msg):
                                    karma_subject = re.search('^[\S]+\-\-', irc_params_msg).group()[0:-2]
                                    karma_subject_score = getobj(KARMA, karma_subject)
                                    if karma_subject_score == None:
                                        karma_subject_score = 0
                                    else:
                                        karma_subject_score = int(karma_subject_score)
                                    setobj(KARMA, karma_subject, karma_subject_score-1)

                                # view karma
                                if re.search('^!karma [\S]+', irc_params_msg):
                                    karma_subject = re.search('^!karma [\S]+', irc_params_msg).group()[7:]
                                    karma_subject_score = getobj(KARMA, karma_subject)
                                    # sharia compliance begin
                                    if re.search('^(islam|muslims?|muzzies?|allah|mohamm?[ea]d)$',
                                    karma_subject, re.IGNORECASE):
                                        karma_subject_score = 'allahuakbar'
                                    # sharia compliance end
                                    ircsend(s, 'PRIVMSG '
                                        + irc_params_channel
                                        + ' :'
                                        + str(karma_subject_score)
                                        + ' is the karma of '
                                        + karma_subject
                                        + '.\r\n')

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

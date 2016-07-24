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
import getpass
import random
import threading

# HI
sys.stderr.write('hi - welcome to albot; the legandary irc bot\n')
sys.stderr.write('that is way better than your mom.\n\n')
sys.stderr.flush()

# CONFIG
VERBOSE = True
HOST = "chat.freenode.net"
PORT = 6667
NICK = "albot"
IDENT = "albot"
REALNAME = "albot"
RECONNECT_SLEEP = 5
PASSWORD = getpass.getpass('gimme yer password:')
CHANNELS = ['#gentoo-chat-exile']

# IRC STATES
INIT_OK = 0
CONNECTION_PROBLEM = 1
COMMAND = 2
PARAMS = 3
CR = 4
INIT_MAYBE = 5

# BOT STATES
HOLYNICKS = ['caveman', 'al-caveman', 'alcaveman', 'mahmoud']
SHITNICKS = ['corvus', 'mom']
TOPICS_CLEAN = {}
TIME_LAST_SHIT = 0
SLEEP = 1
RETALIATING = {}
    

# DISCONNECT
def disco(s):
    sys.stderr.write('error: connection error. disconnecting..')
    sys.stderr.flush()
    s.close()
    state = CONNECTION_PROBLEM
    sys.stderr.write(' ok\n')
    sys.stderr.flush()

# SEND TO IRC SERVER
def ircsend(s, msg):
    if VERBOSE:
        sys.stderr.write('>>>>>>:' + msg)
        sys.stderr.flush()
    s.send(msg.encode('ascii'))

# SEND NOTICES TO STDERR
def notice(msg):
    if VERBOSE:
        sys.stderr.write('>>>>>>:' + msg)
        sys.stderr.flush()

class Retaliation (threading.Thread):
    def __init__(self, s, channel):
        threading.Thread.__init__(self)
        self.s = s
        self.channel = channel

    def run(self):
        # global vars
        global SLEEP
        global RETALIATING

        # ui
        notice('retliation thread started. channel: %s, violation time: %s, current time: %s, sleep: %s --- %s\n'
        % (self.channel, TIME_LAST_SHIT, time.time(), SLEEP, TOPICS_CLEAN))

        # reset sleep if its too large
        if SLEEP > 300:
            SLEEP = 1

        # sleep if needed
        while time.time() < (TIME_LAST_SHIT + SLEEP):
            time.sleep(1)

        # identify new topic
        if self.channel in TOPICS_CLEAN:
            msg = TOPICS_CLEAN[self.channel]
        else:
            msg = '-'

        # perform retaliation
        ircsend(self.s, 'TOPIC' + ' ' + self.channel + ' ' + msg + '\r\n')

        # house keeping
        SLEEP = SLEEP * 1.5
        del(RETALIATING[self.channel])

        # ui
        notice('retliation thread exitting..\n')

# sleep cooler
class Sleepcooler (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # global vars
        while True:
            global SLEEP

            time.sleep(15)
            
            SLEEP = SLEEP - 1.5

            if SLEEP <= 0:
                SLEEP = 1

            notice('SEEP--. SLEEP now = %s\n' % SLEEP)

sleeper = Sleepcooler()
sleeper.start()


# CONNECT
while True:
    sys.stderr.write('connecting..')
    sys.stderr.flush()
    s = socket.socket()
    s.connect((HOST, PORT))
    sys.stderr.write(' ok\n')
    sys.stderr.flush()
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
            tmp = str(s.recv(1024), 'ascii')
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
                                sys.stderr.flush()

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
                                    ircsend(s, 'PRIVMSG ' + channel + ' :' +
                                    'hi - surgical topic sanction on Corvus` is active\r\n')
    

                            if irc_command == 'PRIVMSG':
                                # parse message
                                irc_prefix_nick = irc_prefix[0:irc_prefix.find('!')]
                                irc_params_channel = irc_params[0:irc_params.find(' ')]
                                irc_params_msg = irc_params[irc_params.find(' ')+2:]

                                ## did anyone address albot?
                                #if irc_params_msg.find(NICK) == 0:
                                #    ircsend(s, 'PRIVMSG ' + irc_params_channel
                                #    + ' :' + irc_prefix_nick + ', called me?\r\n')

                            # store existing topic upon joining
                            if irc_command == '332':
                                irc_params_ps = irc_params.split(' ')
                                topic = ' '.join(irc_params_ps[2:])

                                # protect holy nicks
                                for holynick in HOLYNICKS:
                                    if topic.lower().find(holynick) >= 0:
                                        topic = topic.replace(holynick, 'Corvus`')

                                TOPICS_CLEAN[irc_params_ps[1]] = topic

                            # update TOPICS_CLEAN if clean, else purify
                            if irc_command == 'TOPIC':
                                irc_params_ps = irc_params.split(' ')
                                channel = irc_params_ps[0]
                                topic = ' '.join(irc_params_ps[1:])
                                is_pure = True
                                for shitnick in SHITNICKS:
                                    if irc_prefix.lower().find(shitnick) >= 0:
                                        is_pure = False
                                for holynick in HOLYNICKS:
                                    if topic.lower().find(holynick) >= 0:
                                        topic = topic.replace(holynick, 'Corvus`')
                                        is_pure = False

                                if is_pure: # pure case
                                    TOPICS_CLEAN[channel] = topic

                                else: # deficated case
                                    # inqueue for retaliation and set delay
                                    TIME_LAST_SHIT = time.time()
                                    if channel not in RETALIATING:
                                        notice('retaliating..')
                                        retaliate = Retaliation(s, channel)
                                        retaliate.start()
                                        RETALIATING[channel] = True

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
    sys.stderr.flush()
    time.sleep(RECONNECT_SLEEP)

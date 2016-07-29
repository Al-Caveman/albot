# albot005 - the legendary irc bot that is way better than your mom.
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
from numpy import random as random
from getpass import getpass

# HI
sys.stderr.write('hi - welcome to albot; the legandary irc bot\n')
sys.stderr.write('that is way better than your mom.\n\n')
sys.stderr.flush()

# CONFIG
VERBOSE = True
HOST = "irc.freenode.net"
PORT = 6667
NICK = "corvussmom"
IDENT = "corvussmom"
REALNAME = "Vladlena Ivanovsky"
RECONNECT_SLEEP = 5
CHANNELS = ['#gentoo-chat-exile']
MAXNICKLEN = 16
SHITNICK = 'corvus'
HOLYNICKS = ['caveman', 'borz', 'batross', 'mahmo']

# STATES
INIT_OK = 0
CONNECTION_PROBLEM = 1
COMMAND = 2
PARAMS = 3
CR = 4
INIT_MAYBE = 5
random.seed(int(time.time() + 0.5))

# return silly string
def sillystring():
    sillies = ['Need milk?',
        'I am very experienced honey.',
        "Corvus` is actually not my legit son but don't tell hubby.",
        "Sometimes a mom gonna do what a mom gonna do ;)"]
    random.shuffle(sillies)
    return sillies[0]

# return insults about Corvus`
def insultstring():
    insults = ['Honey Corvus`, I always loved you and your Afghani father.',
        'Corvus` never looked Russian though.',
        "Some say that Corvus` looks identical to his Afghani father.",
        "I'm so fat that when I sat on Corvus`'s iPhone it turned into an iPad.",
        "Nothing scares me more than an Afghani with an American stinger.",
        "Corvus` I'm sweet momy, Vladlena Ivanovsky. Why are you trolling bad boy?",
        "I'm so fat that I have mass regardless of whether Higgs Boson exists :(",
        "I never understand why Corvus` hates Afghanies so much. His real father is an Afghani..",
        "Idi syuda Corvus`. Why don't you like your Afghani father? I liked his moves.",
        "I am 7-10k years old"]
    for i in range(0, 100):
        random.shuffle(insults)
    return insults[0]

# SEND TO IRC SERVER
def ircsend(s, msg, more=0):
    delay = len(msg) * float(60)/18000 + random.random()*10 + more
    if VERBOSE:
        sys.stderr.write('>SLEEP:%s\n' % str(delay))
        sys.stderr.flush()
        time.sleep(delay)
        sys.stderr.write('>>>>>>:' + msg)
        sys.stderr.flush()
    s.send(msg)

# CONNECT
while True:
    sys.stderr.write('connecting..')
    sys.stderr.flush()
    s = socket.socket()
    s.connect((HOST, PORT))
    sys.stderr.write(' ok\n')
    sys.stderr.flush()
    ircsend(s, 'NICK ' + NICK + '\r\n')
    ircsend(s, 'USER %s %s tits :%s\r\n' % (IDENT, HOST, REALNAME))
    
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
                sys.stderr.write('error: connection problem. disconnecting.. ')
                sys.stderr.flush()
                s.close()
                sys.stderr.write('ok\n')
                sys.stderr.flush()
                state = CONNECTION_PROBLEM
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

                            # join channels only if motd is done
                            if irc_command == '376':
                                for channel in CHANNELS:
                                    ircsend(s, 'JOIN ' + channel + '\r\n')
                                    ircsend(s, 'PRIVMSG ' + channel
                                    + ' :Hmm my tits are ready. Please shake'
                                    + ' them to make various dairy products,'
                                    + ' or type !help for help (here or in'
                                    + ' private messages). Thank you.\r\n')

                            # too fast nick changing? wait 20 seconds
                            if irc_command == '438':
                                sys.stderr.write('++++++:sleeping 20secs\n')
                                sys.stderr.flush()
                                time.sleep(20)

                            if irc_command == 'PRIVMSG':
                                # parse message
                                nick    = irc_prefix[0:irc_prefix.find('!')]
                                channel = irc_params[0:irc_params.find(' ')]
                                msg     = irc_params[irc_params.find(' ')+2:]

                                # did anyone call my nickname?
                                if msg.find(NICK) == 0:
                                    if channel == NICK:
                                        channel = nick
                                    ircsend(s, 'PRIVMSG ' + channel
                                    + ' :' + nick + '. '
                                    + sillystring()
                                    + ' PM me `!help`.\r\n')

                                # did anyone call Corvus, or Corvus talked?
                                # (only 30% of the time)
                                if msg.lower().find(SHITNICK) >= 0:
                                    if channel == NICK:
                                        channel = nick
                                    if random.random() <= 0.3:
                                        ircsend(s, 'PRIVMSG ' + channel
                                        + ' :' + insultstring() + '\r\n')
                                elif nick.lower().find(SHITNICK) >= 0:
                                    if channel == NICK:
                                        channel = nick
                                    if random.random() <= 0.3:
                                        ircsend(s, 'PRIVMSG ' + channel
                                        + ' :' + insultstring() + '\r\n')

                                # did anyone type !help?
                                if msg.find('!help') == 0:
                                    if channel == NICK:
                                        channel = nick

                                    ircsend(s, 'PRIVMSG ' + channel
                                    + ' :Hi ' + nick + ', my sweetheart.'
                                    + ' ' + sillystring() + '\r\n')

                                    ircsend(s, 'PRIVMSG ' + channel
                                    + ' :I offer you the only'
                                    + ' intersteller-style space-time tunnel'
                                    + ' that is known in the Milky Way (aka'
                                    + ' wormhole).\r\n')

                                    ircsend(s, 'PRIVMSG ' + channel
                                    + ' :Use `!wormhole <text> [#hashtag] to'
                                    + ' send <text> across multiple universes'
                                    + ' using signalling method that is'
                                    + ' specified in #hashtag. If no hashtag'
                                    + ' is specied, then simple sigalling is'
                                    + ' used. If you use the hashtag #tits'
                                    + ' then nickshit signalling is used. If'
                                    + ' you use the hashtag #titsblast then,'
                                    + ' both, nickshit parting signalling is'
                                    + ' used.\r\n')

                                    ircsend(s, 'PRIVMSG ' + channel
                                    + ' :That said, happy intertestical'
                                    + ' journey honey XoxoxoxoxoX!.\r\n')

                                # did anyone type !wormhole?
                                if msg.find('!wormhole') == 0:
                                    # channel when sent in pm?
                                    if channel == NICK:
                                        channel = CHANNELS[0]

                                    # find text and hashtag
                                    text, hashtag = re.match(
                                        '!wormhole +(.*?) *(#[a-z]+)?$', msg
                                    ).groups()

                                    # filter text
                                    for holynick in HOLYNICKS:
                                        text = re.sub(holynick, 'Corvus`', text)

                                    # simple signalling
                                    if hashtag == None:
                                        ircsend(s, 'PRIVMSG ' + channel
                                        + ' :[WORMHOLE] '
                                        + nick
                                        + ' says ==>> ' + text + '\r\n')

                                    # other fancy signallings
                                    elif (hashtag == '#tits') or (hashtag == '#titsblast'):
                                        # channel when sent in pm?
                                        if channel == NICK:
                                            channel = CHANNELS[0]

                                        # sanitify text
                                        text = re.sub('[^\w\s0-9-\[\]]', '', text)
                                        text = re.sub('\s', '_', text)
                                        text_chunks = [text[i:i+16] for i in
                                        range(0, len(text), 16)]

                                        for text_chunk in text_chunks:
                                            # does chunk begin or end by non-letter?
                                            text_chunk = re.sub('^[^a-zA-Z]', '', text_chunk)
                                            text_chunk = re.sub('[^a-zA-Z]$', '', text_chunk)

                                            # nickshit signalling
                                            if hashtag == '#tits':
                                                ircsend(s, 'NICK '
                                                + text_chunk
                                                + '\r\n', 3)

                                            # nickshit nickshit part/join signalling
                                            elif hashtag == '#titsblast':
                                                ircsend(s, 'NICK '
                                                + text_chunk
                                                + '\r\n', 3)

                                                ircsend(s, 'PART ' + channel
                                                + '\r\n')


                                                ircsend(s, 'JOIN ' + channel
                                                + '\r\n')
                                        # revert original nick
                                        ircsend(s, 'NICK '
                                        + NICK
                                        + '\r\n', 3)

                                    # unknown hashtag?
                                    else:
                                        ircsend(s, 'PRIVMSG ' + nick
                                        + ' :Unknown hashtag "'
                                        + hashtag
                                        + '" suka blayd.. Type `!help`.\r\n')


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

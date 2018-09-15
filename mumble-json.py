#!/usr/bin/python

# The server name to display
SERVER_NAME = "My Server"

# edit this to query another server id
SERVER_ID = 1

# provide correct location of slice here
SLICE = '/usr/share/slice/Murmur.ice'

# The port of the ICE connection
ICE_PORT = 6502

##################################################################################
# DO NOT EDIT BEYOND THIS LINE !!! 
##################################################################################

import Ice
import sys

Ice.loadSlice( "", ["-I" + Ice.getSliceDir(), SLICE])
import Murmur

# Init ice
comm = Ice.initialize()
# Let Ice know where to go to connect to mumble
proxy = comm.stringToProxy('Meta -e 1.0:tcp -p ' + str(ICE_PORT))
# Create a dynamic object that allows us to get a programmable interface for Mumble
meta = Murmur.MetaPrx.checkedCast(proxy)

##################################################################################
# Query the Mumble server 
##################################################################################

# Get the server instance from the set of servers.
server = meta.getServer(SERVER_ID)

channelMap = server.getChannels()
userMap = server.getUsers()

##################################################################################
# Init maps for easier lookup 
##################################################################################

channelChildrenMap = dict()
for key, channel in channelMap.iteritems():
    if channel.parent in channelChildrenMap:
        channelChildrenMap[channel.parent].append(channel)
    else:
        channelChildrenMap[channel.parent] = [ channel ] 

usersInChannelMap = dict()
for key, user in userMap.iteritems():
    if user.channel in usersInChannelMap:
        usersInChannelMap[user.channel].append(user)
    else:
        usersInChannelMap[user.channel] = [ user ]

##################################################################################
# Procedure definitions
##################################################################################

def getChannelLinks(channel):
    links=''
    for link in channel.links:
        if links != '':
            links = links + ',' 
        links = links + str(link)
    return links

def printUser(user, tab):
    print tab + '"channel": ' + str(user.channel) + ','
    print tab + '"deaf": ' + str(user.deaf).lower() + ','
    print tab + '"mute": ' + str(user.mute).lower() + ','
    print tab + '"name": "' + user.name + '",'
    print tab + '"selfDeaf": ' + str(user.selfDeaf).lower() + ','
    print tab + '"selfMute": ' + str(user.selfMute).lower() + ','
    print tab + '"session": ' + str(user.session) + ','
    print tab + '"suppress": ' + str(user.suppress).lower() + ','
    print tab + '"userid": ' + str(user.userid)

def printChannelUsers(channel, tab):
    print tab + '"users": ['
    first = True

    if channel.id in usersInChannelMap:
        for user in usersInChannelMap[channel.id]:
            if first == False:
                print tab + ',{'
            else:
                print tab + '{'
                first = False
            printUser(user, tab + '\t')
            print tab + '}'
    print tab + '],'

def printChannelChildren(channel, tab):
    print tab + '"channels": ['
    first = True

    if channel.id in channelChildrenMap:
        for child in channelChildrenMap[channel.id]:
            if first == False:
                print tab + ',{'
            else:
                print tab + '{'
                first = False
            printChannel(child, tab + '\t')
            print tab +  '}'
    print tab + ']'

def printChannel(channel, tab):
    print tab + '"name": "' + channel.name + '",'
    print tab + '"id": ' + str(channel.id) + ','
    #print tab + '"description": "' + channel.description + '",'
    print tab + '"description": "",'
    print tab + '"links": [' + getChannelLinks(channel) + '],'
    print tab + '"parent": ' + str(channel.parent) + ','
    print tab + '"position": ' + str(channel.position) + ','
    print tab + '"temporary": ' + str(channel.temporary).lower() +","

    printChannelUsers(channel, tab )
    printChannelChildren(channel, tab )

def printServer():
    tab = '\t'
    print '{'
    print tab + '"id": ' + str(SERVER_ID) + ','
    print '"name": "' + SERVER_NAME + '",'
    print tab + '"root": '
    first = True
    rootId = -1

    if rootId in channelChildrenMap:
        for channel in channelChildrenMap[rootId]:
            if first == True:
                print tab + '{'
            else:
                print tab + ',{'
                first = False
            printChannel(channel, tab + '\t')
            print tab + '}'
    else:
        print '{}'

    print '}'

##################################################################################
# Print JSON to stdout 
##################################################################################

print 'Content-Type: text/plain'
print
printServer()

##################################################################################
# Close Ice communication 
##################################################################################

if comm:
    comm.destroy()

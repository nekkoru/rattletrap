import requests
import dota2api
import json
import sys
import socket
import string
from time import sleep

#server / channel information

HOST = "irc.what-network.net"
PORT = 6667
NICK = "Rattletrap"
IDENT = "Rattletrap"
REALNAME = "Rattletrap the Clockwerk"
NICKSERV = "changeme" # optional, if your network requires you to register
CHANNEL = "#dota"

s = socket.socket()


api = dota2api.Initialise("E337281DA466818041F26B4AD42F7C4A")

def findmatch(id):
  try:
    match = api.get_match_details(match_id=id)
    #print(json.dumps(match, sort_keys=True, indent=2))
    return match

  except dota2api.src.exceptions.APITimeoutError:
    say("503 API unavailable.")

def parse_match(id):
  match = findmatch(id)
  say("Match id {0}, {1} victory. Dotabuff link: http://www.dotabuff.com/matches/{2}".format(match["match_id"], "Radiant" if match["radiant_win"] else "Dire", match["match_id"]))

def say(message):
  s.send(bytes("PRIVMSG {0} :{1}\r\n".format(CHANNEL, message), "UTF-8"))
  

s.connect((HOST, PORT))
s.send(bytes("NICK {0}\r\n".format(NICK), "UTF-8"))
s.send(bytes("USER {0} {1} bla :{2}\r\n".format(IDENT, HOST, REALNAME), "UTF-8"))
sleep(3)
s.send(bytes("PRIVMSG nickserv :identify {0}\r\n".format(NICKSERV), "UTF-8"))
s.send(bytes("JOIN {0}\r\n".format(CHANNEL), "UTF-8"))


readbuffer = ""

while 1:
  readbuffer=readbuffer+s.recv(1024).decode("utf-8")
  temp = readbuffer.split("\n")
  readbuffer=temp.pop()

  for line in temp:
    line = line.rstrip()
    print(line)
    line = line.split()
    if(line[0]=="PING"):
      s.send(bytes("PONG {0}\r\n".format(line[1]), "UTF-8"))
    elif(line[1]=="PRIVMSG"):

      #Commands start here

      if(line[2]==CHANNEL):
        if(line[3]==":!match"): #all messages start with a colon because of how IRC works
          try:
            val = int(line[4])
          except ValueError:
            say("Wrong match ID.")
          else:
            print("Match requested, ID {0}".format(line[4]))
            parse_match(line[4])


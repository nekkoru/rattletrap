import dota2api
import json
import re
import requests
import socket
import string
import sys
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
data_file = open("data.json", "r+")
ids = json.load(data_file)
api = dota2api.Initialise("E337281DA466818041F26B4AD42F7C4A")

HEROES = api.get_heroes()[heroes]

def findmatch(id):
  try:
    match = api.get_match_details(match_id=id)
    #print(json.dumps(match, sort_keys=True, indent=2))
    return match
  
  except dota2api.src.exceptions.APIError:
    say("No match specified")

  except dota2api.src.exceptions.APITimeoutError:
    say("503 API unavailable.")

def parse_match(id, player_id=False):
  match = findmatch(id)
  say("Match id {0}, {1} victory. Dotabuff link: http://www.dotabuff.com/matches/{2}".format(match["match_id"], "Radiant" if match["radiant_win"] else "Dire", match["match_id"]))
  
  if player_id==True:
    if player_id in match[players]


def say(message):
  s.send(bytes("PRIVMSG {0} :{1}\r\n".format(CHANNEL, message), "UTF-8"))

def name(line):
  clean_name = line.split("!")[0].lstrip(":")
  return clean_name

s.connect((HOST, PORT))
s.send(bytes("NICK {0}\r\n".format(NICK), "UTF-8"))
s.send(bytes("USER {0} {1} bla :{2}\r\n".format(IDENT, HOST, REALNAME), "UTF-8"))
sleep(3)
s.send(bytes("PRIVMSG nickserv :identify {0}\r\n".format(NICKSERV), "UTF-8"))
s.send(bytes("JOIN {0}\r\n".format(CHANNEL), "UTF-8"))


readbuffer = ""

try:
 while 1:
   readbuffer=readbuffer+s.recv(1024).decode("utf-8")
   temp = readbuffer.split("\n")
   readbuffer=temp.pop()

   for line in temp:
     line = line.rstrip()
     line = line.split()
     if(line[0]=="PING"):
       s.send(bytes("PONG {0}\r\n".format(line[1]), "UTF-8"))
     elif(line[1]=="PRIVMSG"):

       #Commands start here

       if(line[2]==CHANNEL):
         if(line[3]==":!commands" or line[3]==":!help"):
           say("Available commands: !lastmatch, !match <match_id>, !setuser <dotabuff_id>")
         if(line[3]==":!lastmatch"): #all messages start with a colon because of how IRC works
           if name(line[0]) in ids:
             matches = api.get_match_history(account_id=ids[name(line[0])], matches_requested=1)
             parse_match(matches["matches"][0]["match_id"])
             print("!lastmatch called by {0} for matchID {1}".format(name(line[0]), matches["matches"][0]["match_id"]))
             #print(json.dumps(matches, sort_keys=True, indent=4))
           else:
             say("User not found. Do !setuser first.")
             print("!lastmatch was called, but {0} is not in the database".format(name(line[0])))
         if(line[3]==":!match"):
           try:
             val = int(line[4])
           except ValueError:
             say("Wrong match ID.")
           else:
             print("Match requested, ID {0}".format(line[4]))
             parse_match(line[4])

         if(line[3]==":!setuser"):
           try:
             line[4] == True
             try:
               val = int(line[4])
             except ValueError:
               say("Wrong Dota ID format. I want your ID from your Dotabuff url, like: https://dotabuff.com/players/<id>")
             else:
               player = name(line[0])
               ids[player] = line[4]
               data_file.seek(0)
               data_file.truncate
               json.dump(ids, data_file)
               say("Alright, your Dota ID is {0}".format(line[4]))
               print("{0} was added to the data file with Dota ID {1}".format(name(line[0]), line[4]))
           except IndexError:
             say("Usage: !setuser <dotabuff_id>")

except KeyboardInterrupt:
  data_file.close()
  sys.exit()
             

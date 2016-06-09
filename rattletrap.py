"""
Rattletrap - a Dota 2 IRC bot.

https://github.com/nekkoru/rattletrap
Edit this file to put in your connection details

"""
import dota2api
import json
import socket
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


S = socket.socket()
data_file = open("data.json", "r+")
ids = json.load(data_file)
API = dota2api.Initialise("E337281DA466818041F26B4AD42F7C4A")

def findmatch(match_id):
    """ returns a match by ID """
    try:
        match = API.get_match_details(match_id=match_id)
        return match

    except dota2api.src.exceptions.APIError:
        say("No match specified")

    except dota2api.src.exceptions.APITimeoutError:
        say("503 API unavailable.")

def parse_match(match_id):
    """ parses the match and figures out whether the username invoking took part in it (WIP) """
    match = findmatch(match_id)
    if match is not None:
        say("Match id {0}, {1} victory. Dotabuff link: "
            "http://www.dotabuff.com/matches/{2}".format(
                match["match_id"],
                "Radiant" if match["radiant_win"] else "Dire",
                match["match_id"]))

def say(message):
    """ says stuff to the channel """
    S.send(bytes("PRIVMSG {0} :{1}\r\n".format(
        CHANNEL, message), "UTF-8"))

def name(mask):
    """ cleans nicknames from the entire host mask """
    clean_name = mask.split("!")[0].lstrip(":")
    return clean_name

# Custom commands start here, triggers below

def commands():
    """ displays the available commands. """
    say("Available commands: !lastmatch, !match <match_id>, !setuser <dotabuff_id>")

def lastmatch(name):
    if name in ids:
        match_id = API.get_match_history(
            account_id=ids[name],
            matches_requested=1)["matches"][0]["match_id"]
        parse_match(match_id)
        print("!lastmatch called by {0} for matchID {1}".format(
            name, match_id))
    else:
        say("User not found. Do !setuser first.")
        print("!lastmatch was called, but {0} is not in the database".format(name(line[0])))

def set_user(name, dotaid):
    ids[name] = dotaid
    data_file.seek(0)
    data_file.truncate
    json.dump(ids, data_file)
    say("Alright, your Dota ID is {0}".format(dotaid)
    print("{0} was added to the data file with Dota ID {1}".format(
        name, dotaid))

S.connect((HOST, PORT))
S.send(bytes("NICK {0}\r\n".format(NICK), "UTF-8"))
S.send(bytes("USER {0} {1} bla :{2}\r\n".format(
    IDENT, HOST, REALNAME), "UTF-8"))
sleep(3)
S.send(bytes("PRIVMSG nickserv :identify {0}\r\n".format(NICKSERV),
             "UTF-8"))
S.send(bytes("JOIN {0}\r\n".format(CHANNEL), "UTF-8"))


readbuffer = ""

try:
    while 1:
        readbuffer = readbuffer + S.recv(1024).decode("utf-8")
        temp = readbuffer.split("\n")
        readbuffer = temp.pop()
        for line in temp:
            line = line.rstrip()
            line = line.split()
            if line[0] == "PING":
                S.send(bytes("PONG {0}\r\n".format(line[1]), "UTF-8"))
            elif line[1] == "PRIVMSG":

       #Command triggers start here

                if line[2] == CHANNEL:
                    if line[3] == ":!commands" or line[3] == ":!help":
                        commands()

                    if line[3] == ":!lastmatch":
                        lastmach(name(line[0]))

                    if line[3] == ":!match":
                        try:
                            val = int(line[4])
                        except ValueError:
                            say("Wrong match ID.")
                        else:
                            print("Match requested, ID {0}".format(line[4]))
                            parse_match(line[4])

                    if line[3] == ":!setuser":
                        try:
                            line[4] == True
                            try:
                                val = int(line[4])
                            except ValueError:
                                say("Wrong Dota ID format. O want your ID from your Dotabuff url,"
                                    " like: https://dotabuff.com/players/<id>")
                            else:
                                set_user(name(line[0], line[4])
                        except IndexError:
                            say("Usage: !setuser <dotabuff_id>")

except KeyboardInterrupt:
    data_file.close()
    sys.exit()

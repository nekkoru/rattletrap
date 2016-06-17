"""
Rattletrap - a Dota 2 IRC bot.

https://github.com/nekkoru/rattletrap
Edit this file to put in your connection details

"""
import dota2api
import json
import re
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
DOTABUFF = re.compile(":http://www.dotabuff.com/matches/\d+")

def find_match(match_id):
    """ returns a match by ID, retries five times in case of API timeout """
    match = None
    r = 5
    while not match and r > 0:
        try:
            match = API.get_match_details(match_id=match_id)
            return match
        
        except dota2api.src.exceptions.APIError:
            r = 0
            say("No match specified")
            
        except dota2api.src.exceptions.APITimeoutError:
            r -= 1
            print("API unavailable, retrying...")
            sleep(1)
            say("503 API unavailable.")

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

def last_match(name):
    if name in ids:
        try:
            match_id = API.get_match_history(
                account_id=ids[name],
                matches_requested=1)["matches"][0]["match_id"]
        except dota2api.src.exceptions.APIError:
            say("Couldn't retrieve match. Is your profile set to private?");
        except dota2api.src.exceptions.APITimeoutError:
            say("503 API unavailable.")
        else:
            parse_match(match_id, name)
            print("!lastmatch called by {0} for matchID {1}".format(
                name, match_id))
    else:
        say("User not found. Do !setuser first.")
        print("!lastmatch was called, but {0} is not in the database".format(name))

def parse_match(match_id, name=""):
    """ parses the match and figures out whether the username invoking took part in it (WIP) """
    match = find_match(match_id)
    if match is not None:
        say("Match id {0}, {1} victory. Dotabuff link: "
            "http://www.dotabuff.com/matches/{2}".format(
                match["match_id"],
                "Radiant" if match["radiant_win"] else "Dire",
                match["match_id"]))
        #check whether player calling the match was in the game
        if name != "":
            for player in match["players"]:
                if player["account_id"] == int(ids[name]):

                    result = ""
                    if match["radiant_win"] == True and len(str(player["player_slot"])) == 1:
                        result = "won"
                    elif match["radiant_win"] == False and len(str(player["player_slot"])) ==3:
                        result = "won"
                    else:
                        result = "lost"
                    
                    say("You played {0}, {1} the game and went {2}/{3}/{4}. Level {5}, KDA {6}, "
                        "{7} LH / {8} DN, {9} GPM, {10} XPM, {11} HD, {12} TD".format(
                            player["hero_name"],
                            result,
                            player["kills"],
                            player["deaths"],
                            player["assists"],
                            player["level"],
                            round(player["kills"] + player["assists"] / player["deaths"], 2),
                            player["last_hits"],
                            player["denies"],
                            player["gold_per_min"],
                            player["xp_per_min"],
                            player["hero_damage"],
                            player["tower_damage"]))
                    items = []
                    for i in range(5):
                        if player.get("item_{}_name".foramt(i)) is not None:
                            items.append(player["item_{}_name".format(i)])
                    say("Your items were: {}".format(", ".join(items)))

def set_user(name, dotaid):
    ids[name] = dotaid
    data_file.seek(0)
    data_file.truncate
    json.dump(ids, data_file)
    say("Alright, your Dota ID is {0}".format(dotaid))
    print("{0} was added to the data file with Dota ID {1}".format(
        name, dotaid))


if __name__ == '__main__':
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
                                last_match(name(line[0]))
                                
                        if line[3] == ":!match":
                            try:
                                val = int(line[4])
                            except ValueError or IndexError:
                                say("Wrong match ID.")
                            else:
                                print("Match requested, ID {0}".format(line[4]))
                                parse_match(line[4], name(line[0]))
                                        
                        if DOTABUFF.match(line[3]):
                            url = line[3].split("/")
                            print("Match requested, ID {0}".format(url[4]))
                            parse_match(url[4], name(line[0]))
                                            
                        if line[3] == ":!setuser":
                            try:
                                line[4] == True
                                try:
                                    val = int(line[4])
                                except ValueError:
                                    say("Wrong Dota ID format. I want your ID from your Dotabuff url,"
                                        "like: https://dotabuff.com/players/<id>")
                                else:
                                    set_user(name(line[0]), line[4])
                            except IndexError:
                                say("Usage: !setuser <dotabuff_id>")
                                                    
    except KeyboardInterrupt:
        data_file.close()
        sys.exit()

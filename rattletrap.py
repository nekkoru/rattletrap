import requests
import dota2api
import json

api = dota2api.Initialise("E337281DA466818041F26B4AD42F7C4A")

def findmatch(id):
  try:
    match = api.get_match_details(match_id=id)
    #print(json.dumps(match, sort_keys=True, indent=2))
    return match

  except dota2api.src.exceptions.APITimeoutError:
    print("503 API unavailable.")

def parse_match(id):
  match = findmatch(id)
  print("Match id {0}, {1} victory. Dotabuff link: http://www.dotabuff.com/matches/{2}".format(match["match_id"], "Radiant" if match["radiant_win"] else "Dire", match["match_id"]))
    
parse_match(2349995050)

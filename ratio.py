# coding: latin-1
import pymongo
from pymongo import MongoClient
from operator import itemgetter

client = MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['players']
uselessStats = set(["Hustle", "Pick & roll defense IQ", "Passing vision", "_id", "name", "overall", "Pass perception", "Shot IQ", "On-ball defense IQ", "Low post defense IQ"])
players = []
divisorPrinted = False
cursor = db.find()
for player in cursor:
    if int(player["overall"]) > 73:
        avgStats = 0
        divisor = 0
        for stat in player:
            if not stat in uselessStats:
                avgStats += player[stat]
                divisor+=1
        if not divisorPrinted:
            divisorPrinted = True
        avgStats /= divisor
        ratio = avgStats / float(player["overall"])
        playerObj = {
            "ratio" : round(ratio, 3),
            "name" : player["name"],
            "overall" : player["overall"]
        }
        players.append(playerObj)

# print players
# newlist = players.sort(key=lambda data: players["ratio"])
newlist = sorted(players, key=itemgetter('ratio'), reverse=True)
# players.sort()
# print newlist



f = open("highRatio", "w")
for item in newlist:
    f.write(str(item["name"].encode("utf-8")) + " " + str(item["overall"]) + " " + str(item["ratio"]))
    f.write('\n')
f.close()

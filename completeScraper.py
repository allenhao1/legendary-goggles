#!python2
#coding: utf8
from bs4 import BeautifulSoup
import requests
import pymongo
from pymongo import MongoClient
import re
import sys

client = MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['players2']

#Both Nene's, 1016 Bosh and 2328 Kyrie don't work. Have to manually add
indexUrl = "http://www.2kmtcentral.com/17/players/page/"
playerLinks = []
valid = False
x = 0
playerErr = [];
while(valid):
    request = requests.get(indexUrl + str(x))
    html = request.text;
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find_all( 'a', class_='name', href=True)
    if len(content) == 0:
        print "No more players"
        valid = False
        break
    # print content
    for a in content:
        url = a['href'].encode('utf-8') #Have to encode and decode because Nene has a circumflex in his name
        playerLinks.append(url)
    print "Done with " + str(x+1) + " pages"
    x+=1
# playerLinks = open("playerLinks", "r")
# str(len(playerLinks))
positionConvert = {"PG": 1, "SG" : 2, "SF" :3, "PF" : 4, "C" : 5 }
counter = 0
playerObjList = []
for link in playerLinks:
    try:
        html = requests.get(link).text
        soup = BeautifulSoup(html, 'html.parser')
        playerObj = {}
        playerObj["_id"] = int(link.split("/")[5])
        playerObj["Name"] = str(soup.find("table").find("td").text)
        playerObj["Overall"] = int(soup.find_all(class_="overall")[0].text)
        # table = soup.find("table").find_all("td")
        # pos = str(table[4].text.replace(u'\ufeff', '').encode()).split("/")
        # playerObj["Position"] = int(positionConvert[str(pos[0]).strip()])
        # if len(pos) == 2:
            # playerObj["Secondary position"] = int(positionConvert[str(pos[1]).strip()])
        #some bs4 tables get wonky
        for elem in soup(text=re.compile(r'[5-7]\'1?[0-9]\"')):
            heightStr =  elem.parent.text
            break
        heightStr = re.split("[^0-9]", heightStr)
        feet = heightStr[0]
        inches = heightStr[1]
        playerObj["Height"] = int(feet) * 12 + int(inches)
        # Look through blocks of attributes and parse out rating and name of rating
        for attributes in soup.find_all(class_="attribute-list"):
            for attributes in attributes.find_all("li"):
                #2kmtcentral has some hidden stuff when you shrink the screen
                regex = "([Dd]ef|[Oo]ff)\." #Match def. or off. or uppercase versions
                stats = re.sub(regex, "", attributes.text)
                statVal = int(stats[:2]) #Actual rating i.e. 89
                statName = str(stats[3:]) #Type of stat i.e. contested 3
                playerObj[statName] = statVal
        # db.insert_one(playerObj)
        playerObjList.append(playerObj)
        counter +=1
        if counter % 100 == 0:
            print str(counter) + " players added out of " + str(totalPlayers) + " players"
    except Exception,e:
        playerErr.append(link);
        print str(e)
        print sys.exc_traceback.tb_lineno
        # print link.split("/")[6] + " had an error"
        print link
print str(counter) + " players added"
if len(playerErr) == 0:
    for player in playerObjList:
        db.insert_one(player)
for link in playerErr:
    print link;
playerLinks.close()

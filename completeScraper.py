#!python2
#coding: latin-1
from bs4 import BeautifulSoup
import requests
from db import db
import re
import sys
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['try2']

##Both Nene's, 1016 Bosh and 2328 Kyrie don't work. Have to manually add
# indexUrl = "http://www.2kmtcentral.com/17/players/page/"
# playerLinks = []
# valid = True
# x = 0
playerErr = []
# while(valid):
#     request = requests.get(indexUrl + str(x))
#     html = request.text;
#     soup = BeautifulSoup(html, 'html.parser')
#     content = soup.find_all( 'a', class_='name', href=True)
#     if len(content) == 0:
#         print "No more pages"
#         valid = False
#         break
#     for a in content:
#         url = a['href'].encode('utf-8') #Have to encode and decode because Nene has a circumflex in his name
#         playerLinks.append(url)
#     print "Done with " + str(x+1) + " pages"
#     x+=1
#     print x

# playerLinks = open('playerLinks.txt', 'r')
playerLinks = ['http://2kmtcentral.com/17/players/8027/adrian-dantley']
counter = 0
playerObjList = []
posErr = open("playerPosErr", "w")
# totalPlayers = len(playerLinks)
for link in playerLinks:
    try:
        html = requests.get(link).text
        soup = BeautifulSoup(html, 'html.parser')
        playerObj = {}
        playerObj["_id"] = int(link.split("/")[5])
        playerObj["Name"] = str(soup.find("table").find("td").text.encode('UTF-8'))
        playerObj["Overall"] = int(soup.find_all(class_="overall")[0].text)
        pos = soup.find("span", "position-primary")
        # print pos
        # # Onyx cards don't have position-primary. Have to check old school.
        # # Modularize later
        if pos != None:
            playerObj["Position"] = pos.text
            secondary = soup.find("sup", "position-secondary")
            if secondary != None:
                playerObj["Secondary position"] = secondary.text
        else:
            pos = soup.find(class_='table-striped').find_all('td')[3]
            positions = pos.text.split('/')
            playerObj['Position'] = positions[0]
            if len(positions) > 1 :
                playerObj['Secondary position'] = positions[1]
        # some bs4 tables get wonky
        for elem in soup(text=re.compile(r'[5-7]\'1?[0-9]\"')):
            heightStr =  elem.parent.text
            break
        heightStr = re.split("[^0-9]", heightStr)
        feet = heightStr[0]
        inches = heightStr[1]
        playerObj["Height"] = int(feet) * 12 + int(inches)
        # Look through blocks of attributes and parse out rating and name of rating
        playerObj['Overall'] = int(soup.find(class_='attribute-header').text[:2])
        for attributes in soup.find(class_='container-attributes').find_all(class_="attribute"):
            #2kmtcentral has some hidden stuff when you shrink the screen
            regex = "([Dd]ef|[Oo]ff)\." #Match def. or off. or uppercase versions
            stats = re.sub(regex, "", attributes.text)
            statVal = int(stats[:2]) #Actual rating i.e. 89
            # Gotta account for on-ball d and pick & roll
            statName = str(re.search(r'\d\d((\s[^\+]+)+)', stats).group(1)).strip() #Type of stat i.e. contested 3
            playerObj[statName] = statVal
        # db.insert_one(playerObj)
        print playerObj['Name']
        playerObjList.append(playerObj)
        print playerObj
        counter +=1
        if counter % 100 == 0:
            print str(counter) + " players added"
    except Exception, e:
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
    print link
# playerLinks.close()

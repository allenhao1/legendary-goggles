# coding: latin-1
from bs4 import BeautifulSoup
import requests
import re
import urllib2
from db import db

#TODO add optional adding by id


#read links
playerLinks = open("playerLinks", "r")

# link = "file:///Users/Allen/legendary-goggles/hgrant.html"

# html = urllib2.urlopen(link)
positionConvert = {"PG": 1, "SG" : 2, "SF" :3, "PF" : 4, "C" : 5 }
#Both Nene's, 1016 Bosh and 2328 Kyrie don't work
playerErr = []
for link in playerLinks:
        try:
            html = requests.get(link).text
            soup = BeautifulSoup(html, 'html.parser')
            playerObj = {}
            playerObj["_id"] = int(link.split("/")[5])
            playerObj["Name"] = str(soup.find("table").find("td").text)
            playerObj["Overall"] = int(soup.find_all(class_="overall")[0].text)
            table = soup.find("table").find_all("td")
            pos = str(table[4].text.replace(u'\ufeff', '').encode()).split("/")
            playerObj["Position"] = int(positionConvert[str(pos[0]).strip()])
            if len(pos) == 2:
                playerObj["Secondary position"] = int(positionConvert[str(pos[1]).strip()])
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
            counter +=1
            if counter % 100 == 0:
                print str(counter) + " players added out of " + str(totalPlayers) + " players"
        except Exception,e:
            playerErr.append(link);
            print str(e)
            # print link.split("/")[6] + " had an error"
            print link
print str(counter) + " players added out of " + str(totalPlayers) + " players"
for link in playerErr:
    print link;
playerLinks.close()

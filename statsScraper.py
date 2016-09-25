from bs4 import BeautifulSoup
import urllib2
import pymongo
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['players']
with open('playerLinks') as f:
    links = f.readlines()
counter = 0;
for link in links:
        try:
            link = link.replace("\n", "")
            playerObj = {}
            html = urllib2.urlopen(link);
            soup = BeautifulSoup(html, 'html.parser')

            #Get initial data
            playerObj["_id"] = link.split("/")[5]
            playerObj["name"] = soup.find("table").find("td").text
            playerObj["overall"] = soup.find_all(class_="overall")[0].text

            # Look through blocks of attributes and parse out rating and name of rating
            for attributes in soup.find_all(class_="attribute-list"):
                for attributes in attributes.find_all("li"):
                    #2kmtcentral has some hidden stuff when you shrink the screen
                    stats = attributes.text.replace("([Dd]ef.|[Oo]ff).", "")
                    print stats
                    statVal = int(stats[:2]) #Actual rating i.e. 89
                    statName = str(stats[3:]) #Type of stat i.e. contested 3
                    playerObj[statName] = statVal
            db.insert_one(playerObj)
            print playerObj["name"]
            counter +=1
            print counter + " players added out of " + links.length "players"
        except Exception,e:
            print str(e)
            print link.split("/")[6] + " had an error"

# coding: latin-1
from bs4 import BeautifulSoup
import requests
import pymongo
from pymongo import MongoClient
import re

client = MongoClient('mongodb://localhost:27017/')
db = client['2kdb']['players']

#Both Nene's, 1016 Bosh and 2328 Kyrie don't work. Have to manually add
indexUrl = "http://www.2kmtcentral.com/17/players/page/"
playerLinks = []
valid = True
x = 0
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
for link in playerLinks:
        try:
            link = link.replace("\n", "")
            playerObj = {}
            html = requests.get(link).text
            soup = BeautifulSoup(html, 'html.parser')

            #Get initial data
            playerObj["_id"] = link.split("/")[5]
            playerObj["name"] = soup.find("table").find("td").text
            playerObj["overall"] = soup.find_all(class_="overall")[0].text

            # Look through blocks of attributes and parse out rating and name of rating
            for attributes in soup.find_all(class_="attribute-list"):
                for attributes in attributes.find_all("li"):
                    #2kmtcentral has some hidden stuff when you shrink the screen
                    regex = "([Dd]ef|[Oo]ff)\." #Match def. or off. or uppercase versions
                    stats = re.sub(regex, "", attributes.text)
                    statVal = int(stats[:2]) #Actual rating i.e. 89
                    statName = str(stats[3:]) #Type of stat i.e. contested 3
                    playerObj[statName] = statVal
            db.insert_one(playerObj)
            print playerObj["name"]
            counter +=1
            print str(counter) + " players added out of " + str(len(links)) + " players"
        except Exception,e:
            print str(e)
            print link.split("/")[6] + " had an error"

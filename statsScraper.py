from bs4 import BeautifulSoup
import urllib2
import pymongo
from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
url = "file:///Users/Allen/legendary-goggles/hgrant.html"
db = client['2kdb']['players']
with open('playerLinks') as f:
    links = f.readlines()

for link in links:
        link = link.replace("\n", "")
        html = urllib2.urlopen(url);
        _id = link.split("/")[5]
        name = link.split("/")[6]
        print _id + " "  + name
playerObj = {}
html = urllib2.urlopen(url);
soup = BeautifulSoup(html, 'html.parser')
playerObj["_id"] = url.split("/")[5]
playerObj["name"] = url.split("/")[6]
playerObj["overall"] = soup.find_all(class_="overall")[0].text

#Look through blocks of attributes and parse out rating and name of rating
for attributes in soup.find_all(class_="attribute-list"):
    for attributes in attributes.find_all("li"):
        stats = str(attributes.text)

        statVal = int(stats[:2]) #Actual rating i.e. 89
        statName = str(stats[3:]) #Type of stat i.e. contested 3
        playerObj[statName] = statVal
print playerObj

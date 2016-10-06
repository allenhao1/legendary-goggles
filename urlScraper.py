
from bs4 import BeautifulSoup
import requests
import re

indexUrl = "http://www.2kmtcentral.com/17/players/page/"
handle = open("playerLinks", "w")
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
            handle.write(url + "\n")
        print "Done with " + str(x+1) + " pages"
        x+=1
handle.close()

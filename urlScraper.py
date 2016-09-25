
from bs4 import BeautifulSoup
import urllib2
indexUrl = "http://www.2kmtcentral.com/17/players/page/"
handle = open("playerLinks", "w")
for x in range(0,34):
        html = urllib2.urlopen(indexUrl + str(x));
        soup = BeautifulSoup(html, 'html.parser')
        content = soup.find_all( 'a', class_='name', href=True)
        # print content
        for a in content:
            url = a['href'].encode('utf-8') #Have to encode and decode because Nene has a circumflex in his name
            handle.write(url + "\n")
        print "Done with " + str(x+1) + " out of 34 pages"
handle.close()

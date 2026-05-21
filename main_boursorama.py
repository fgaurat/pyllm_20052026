import requests
from bs4 import BeautifulSoup
from pprint import pprint
import time

def main():
    code_isins = ["fr0000054900","FR0000073272"]

    for code_isin in code_isins:
        url = f"https://www.boursorama.com/recherche/ajax?query={code_isin}"
        resp = requests.get(url)
        with open('tf1.html','w') as f:
            f.write(resp.text)

        soup = BeautifulSoup(resp.text, 'html.parser')

        s = r"div.topbar-searchbar__symbols-market > div.topbar-searchbar__symbols-market--tradable.o-vertical-interval-bottom-large\@sm-max.o-vertical-interval-top\@sm-max > div > li > a > div > div.u-3\/5\@md-min > div:nth-child(1) > span"
        d = soup.select(s)
        print(d[0].string)
        time.sleep(2)

if __name__=='__main__':

    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
    }

    url = "https://artisans-isolation-combles.fr/"
    resp = requests.get(url,headers=headers)
    main()

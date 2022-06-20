import requests
import urllib.request
from bs4 import BeautifulSoup
import time

class DrawceptionScraper:
    def __init__(self, url="https://stage.drawception.com"):
        self.base_url = url.strip('/')
    
    def get_panel_svg(self, sessionid, panelid):
        """Gets the svg from drawception, given the panel id.

        Getting svg images requires a session cookie for images created before
        2021-12-17.
        """
        url = self.base_url + "panel/getsvg.json"
        cookie = {"PHPSESSID": sessionid}
        request = {'panelid': panelid}
        page = requests.post(url, json=request, cookies=cookie)
        if page.status_code != 200:
            return ""
        else:
            return page.text

    def download_panel_from_id(self, panel_id, folder="./images/"):
        """Downloads the panel image from drawception, given the panel id and saves
        it into the specified folder.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        url = self.base_url + "/panel/drawing/" + panel_id + "/1/"
        self.download_panel_from_url(url, folder)

    def download_panel_from_url(self, panel_url, folder="./images/"):
        """Downloads the panel image from drawception, given the panel page link and saves
        it into the specified folder.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        page = requests.get(panel_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        image = soup.find_all('img', class_="gamepanel-minsize gamepanel-shadow img-responsive")[0]
        src = image['src']
        name = image['alt']
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        if "http" in src:
            # Panel is not partially broken.
            urllib.request.urlretrieve(src, folder + name + ".png")
        else:
            # Panel is partially broken.
            urllib.request.urlretrieve(src, folder + name + ".svg")
        
    def get_drawing_links_from_public_games(self, profile, page):
        """Gets all the links to drawings from the public games page. The profile link should be a numeric 
        player id or an url to the main page of the user profile.
        """
        url = profile
        if profile.isdecimal():
            url = self.base_url + "/player/" + str(profile) + "/1/"
        url += "games/" + str(page) + "/"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        a_tags = soup.find_all('a', class_="btn btn-sm btn-bright")
        links = []
        for tag in a_tags:
            links.append(self.base_url + tag['href'])
        return links

if __name__ == "__main__":
    
    session_f = open("sessionid", 'r')
    sessionid = session_f.readline()
    session_f.close()
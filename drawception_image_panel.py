import requests
from bs4 import BeautifulSoup
import re
import logging
from dateutil.parser import parse as parse_date
import urllib.request

class DrawceptionImagePanel:
    def __init__(self, url):
        self.url = url
        if self.url[-1] != "/":
            self.url += "/"
        self.id = None
        self.author = None
        self.creation_date = None
        self.time_spent = None
        self.image_src = None
        self.image_name = None
    
    @staticmethod
    def create_panel_details(url):
        panel = DrawceptionImagePanel(url)
        panel.set_panel_details()
        return panel

    def set_panel_details(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            image = soup.find('img', class_="gamepanel-minsize gamepanel-shadow img-responsive")
            self.id = re.match(".*drawing/(.+)/.*/", self.url)[1]
            details = soup.find("p", class_="lead")
            self.author = str(details.find("a").contents[0])
            time_details = str(details.find("small").contents[0])
            time_re_groups = re.match("In (\\d*) minutes (\\d*) seconds on (.+)", time_details)

            date = None
            try:
                if time_re_groups == None:
                    # Games from 2012 did not record time spent data.
                    date = time_details
                else:
                    minutes = int(time_re_groups[1])
                    seconds = int(time_re_groups[2])
                    self.time_spent = seconds + (60*minutes)
                    date = time_re_groups[3]
                self.creation_date = parse_date(date)
            except Exception:
                logging.warn("Error during parsing string {}".format(time_details))

            self.image_src = image['src']
            self.image_name = image['alt']
            return True
        else:
            logging.error("Unable to access {}. HTTP response: {}".format(self.url, page.status_code))
            return False
    
    @staticmethod
    def download_drawing_from_id(panel_id, base_url="https://stage.drawception.com", folder="./images/"):
        """Downloads the panel image from drawception, given the panel id and saves
        it into the specified folder.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        if folder[-1] != "/":
            folder += "/"
        url = base_url + "/panel/drawing/" + panel_id + "/1/"
        DrawceptionImagePanel.download_drawing_from_url(url, folder)
    
    @staticmethod
    def download_drawing_from_url(url, folder="./images/"):
        """Downloads the panel image from drawception given a direct url to the panel page.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        if folder[-1] != "/":
            folder += "/"
        page = requests.get(url)
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
    
    def download_drawing(self, folder="./images/"):
        """Class method to download the panel image from drawception.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        if folder[-1] != "/":
            folder += "/"
        if self.image_src == None:
            if self.set_panel_details() == False:
                logging.error("Unable to download image from {}".format(self.url))
        
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        if "http" in self.image_src:
            # Panel is not partially broken.
            urllib.request.urlretrieve(self.image_src, folder + self.image_name + ".png")
        else:
            # Panel is partially broken.
            urllib.request.urlretrieve(self.image_src, folder + self.image_name + ".svg")

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

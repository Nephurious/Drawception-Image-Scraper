import requests
from bs4 import BeautifulSoup
import re
import logging
from dateutil.parser import parse as parse_date
import urllib.request
import urllib.parse
import urllib.error
import os

class DrawceptionImagePanel:
    def __init__(self, url):
        self.url = url
        if url[-1] != '/':
            self.url += '/'
        self.id = None
        self.name = None
        self.author = None
        self.creation_date = None
        self.time_spent = None
        self.image_src = None
        self.image_alt = None
    
    @staticmethod
    def create_panel_details(url):
        panel = DrawceptionImagePanel(url)
        panel.set_panel_details()
        return panel

    def parse_time_details(self, time_details):
        try:
            time_re_groups = re.match("In( \\d+ minutes?)?( \\d+ seconds?)?.*on (.+)", time_details)
            if time_re_groups != None:
                time = 0
                if time_re_groups[1] != None:
                    time += 60 * int(time_re_groups[1].split()[0].strip())
                if time_re_groups[2] != None:
                    time += int(time_re_groups[2].split()[0].strip())
                self.time_spent = time
                self.creation_date = parse_date(time_re_groups[3])
            else:
                # Games from 2012 did not record time spent data.
                self.creation_date = parse_date(time_details)
        except Exception as e:
            logging.error("Error during parsing string \"{}\"".format(time_details))

    def set_panel_details(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            image = soup.find('img', class_="gamepanel-minsize gamepanel-shadow img-responsive")
            url_re = re.match(".*drawing/([^/]+)/([^/]*)", self.url)
            self.id = url_re[1]
            self.name = url_re[2]
            details = soup.find("p", class_="lead")
            self.author = str(details.find("a").contents[0])
            time_details = str(details.find("small").contents[0])
            self.parse_time_details(time_details)
            self.image_src = image['src']
            self.image_alt = image['alt']
            return True
        else:
            logging.error("Unable to access \"{}\". HTTP response: {}".format(self.url, page.status_code))
            return False
    
    @staticmethod
    def download_drawing_from_id(panel_id, base_url="https://stage.drawception.com/", directory="./images/"):
        """Downloads the panel image from drawception, given the panel id and saves
        it into the specified directory.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        url = base_url + "panel/drawing/" + panel_id + "/1/"
        url = urllib.parse.urljoin(base_url, "panel/drawing/")
        url = urllib.parse.urljoin(url, str(panel_id))
        url = urllib.parse.urljoin(url, "/1/")
        DrawceptionImagePanel.download_drawing_from_url(url, directory)
    
    @staticmethod
    def download_drawing_from_url(url, directory="./images/"):
        """Downloads the panel image from drawception given a direct url to the panel page.
        Image is saved with the name "[id]_[image_name].[extension]".

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        image = soup.find_all('img', class_="gamepanel-minsize gamepanel-shadow img-responsive")[0]
        src = image['src']
        name = re.match(".*drawing/([^/]+)/([^/]*)", url)[2]
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        filename = ""
        if "http" in src:
            # Panel is not partially broken.
            filename = os.path.join(directory, name + ".png")
        else:
            # Panel is partially broken.
            filename = os.path.join(directory, name + ".svg")
        if os.path.exists(filename):
            logging.warn("File \"{}\" exists. Skipping.".format(filename))
        else:
            try:
                urllib.request.urlretrieve(src, filename)
                return True
            except urllib.error.HTTPError as e:
                logging.error("Unable to get \"{}\". Code: {}".format(e.geturl(), e.getcode()))
                return False
    
    def download_drawing(self, directory="./images/"):
        """Class method to download the panel image from drawception.

        Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
        due to an access denied bug. It is only possible to download svg images.
        """
        if self.image_src == None:
            if self.set_panel_details() == False:
                logging.error("Unable to download image from \"{}\"".format(self.url))
        
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        filename = ""
        if "http" in self.image_src:
            # Panel is not partially broken.
            filename = os.path.join(directory, self.id + '_' + self.name + ".png")
        else:
            # Panel is partially broken.
            filename = os.path.join(directory, self.id + '_' + self.name + ".svg")
        if os.path.exists(filename):
            logging.warn("File \"{}\" exists. Skipping.".format(filename))
        else:
            try:
                urllib.request.urlretrieve(self.image_src, filename)
                return True
            except urllib.error.HTTPError as e:
                logging.error("Unable to get \"{}\". Code: {}".format(e.geturl(), e.getcode()))
                return False
    
    def get_panel_details(self, include_img_src=False):
        """Returns a dictionary containing panel details.

        NOTE: Drawception images created after 2021-12-17 are
        partially broken. These images use data urls that encode
        svg images.
        """
        details = {'id':self.id,
                'name':self.image_alt,
                'name_file_safe':self.name,
                'author':self.author,
                'creation_date':self.creation_date,
                'time_spent':self.time_spent,
                'panel_url':self.url}
        if include_img_src:
            details['img_src'] = self.image_src
        return details
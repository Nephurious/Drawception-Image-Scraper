import requests
from bs4 import BeautifulSoup
import re
import logging
from dateutil.parser import parse as parse_date

class DrawceptionImagePanel:
    def __init__(self, url):
        self.url = url
        self.id = None
        self.author = None
        self.creation_date = None
        self.time_spent = None
        self.image_src = None
        self.image_name = None
    
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
                self.creation_date = parse_date(date).strftime("%Y-%m-%d")
            except Exception:
                logging.warn("Error during parsing string {}".format(time_details))

            self.image_src = image['src']
            self.image_name = image['alt']
            return True
        else:
            logging.error("Unable to access {}. HTTP response: {}".format(self.url, page.status_code))
            return False
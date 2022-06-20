import requests
from bs4 import BeautifulSoup
import re
import logging

class DrawceptionPlayer:
    def __init__(self, url):
        self.url = url
        self.id = None
        self.name = None
        self.num_drawings = None
        self.num_captions = None
        self.followers = None
        self.following = None
        self.total_games = None
        self.total_emotes = None
        self.drawings = []

    def set_player_details(self):
        page = requests.get(self.url)
        if page.status_code == 200:
            self.id = re.match(".*player/(.+)/.*/", self.url)[1]
            soup = BeautifulSoup(page.content, 'html.parser')
            player_statistics = soup.find('p', class_="clear-bot").contents[0].strip()
            player_statistics_re = re.match("(.+) has drawn ([0-9,]+)[^0-9,]+\
([0-9,]+)[^0-9,]+([0-9,]+)[^0-9,]+([0-9,]+)[^0-9,]+\
([0-9,]+)[^0-9,]+([0-9,]+)", player_statistics)
            try:
                self.name = player_statistics_re[1]
                self.num_drawings = int(player_statistics_re[2].replace(',', ''))
                self.num_captions = int(player_statistics_re[3].replace(',', ''))
                self.total_games = int(player_statistics_re[4].replace(',', ''))
                self.following = int(player_statistics_re[5].replace(',', ''))
                self.followers = int(player_statistics_re[6].replace(',', ''))
                self.total_emotes = int(player_statistics_re[7].replace(',', ''))
            except Exception:
                logging.error("Error during parsing string: {}".format(player_statistics))
            return True
        else:
            logging.error("Unable to access {}. \
                           HTTP response: {}".format(self.url, page.status_code))
            return False

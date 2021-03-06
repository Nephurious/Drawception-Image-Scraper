import time
import requests
from bs4 import BeautifulSoup
import re
import logging
import urllib.parse

class DrawceptionPlayer:
    __LOGGER = logging.getLogger("scraper.player")

    def __init__(self, url):
        self.url = url
        if url[-1] != '/':
            self.url += '/'
        self.id = None
        self.name = None
        self.name_filesafe = None
        self.num_drawings = None
        self.num_captions = None
        self.followers = None
        self.following = None
        self.total_games = None
        self.total_emotes = None
        self.drawings = set()

    def set_player_details(self):
        """Visits the player page to set the attributes of this object."""
        page = requests.get(self.url)
        self.url = page.url # Set the self url to be the final url after redirects
        if page.status_code == 200:
            self.id = re.match(".*player/([^/]+)/([^/]*)", self.url)[1]
            self.name_filesafe = re.match(".*player/([^/]+)/([^/]*)", self.url)[2]
            soup = BeautifulSoup(page.content, 'html.parser')
            player_statistics = soup.find('p', class_="clear-bot").contents[0].strip()
            player_statistics_re = re.match("(.+) has drawn ([0-9,]+)[^0-9,]+\
([0-9,]+)[^0-9,]+([0-9,]+)[^0-9,]+([0-9,]+)[^0-9,]+\
([0-9,]+)[^0-9,]*([0-9,]*)", player_statistics)
            try:
                self.name = player_statistics_re[1]
                self.num_drawings = int(player_statistics_re[2].replace(',', ''))
                self.num_captions = int(player_statistics_re[3].replace(',', ''))
                self.total_games = int(player_statistics_re[4].replace(',', ''))
                self.following = int(player_statistics_re[5].replace(',', ''))
                self.followers = int(player_statistics_re[6].replace(',', ''))
                if len(player_statistics_re[7]) == 0:
                    # Occurs when players have not received a single emote
                    self.total_emotes = 0
                else:
                    self.total_emotes = int(player_statistics_re[7].replace(',', ''))
            except Exception:
                self.__LOGGER.error("Error during parsing string: {}".format(player_statistics))
            return True
        else:
            self.__LOGGER.error("Unable to access {}. \
                           HTTP response: {}".format(self.url, page.status_code))
            return False

    @staticmethod
    def get_drawing_links_from_url(url):
        """Gets all the links to drawings from the given url. 

        Returns None when there is an error, a redirect, or when the page returns
        'Nothing here yet'.
        """
        if url[-1] != '/':
            url += '/'
        page = requests.get(url)
        if page.url != url:
            DrawceptionPlayer.__LOGGER.error("Redirected from {} to {}. Unable to get links.".format(url, page.url))
            return None
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, 'html.parser')
            if len(soup.find('div', class_="thumbpanel-container").contents) == 1:
                if soup.find('div', class_="thumbpanel-container").find('div') == None:
                    return None
            url_split = list(urllib.parse.urlsplit(url))
            a_tags = soup.find_all('a', class_="btn btn-sm btn-bright")
            links = []
            for tag in a_tags:
                url_split[2] = tag['href']
                links.append(urllib.parse.urlunsplit(url_split))
            return links
        else:
            DrawceptionPlayer.__LOGGER.error("Unable to access {}. HTTP response: {}".format(url, page.status_code))
            return None
    
    def scrape_drawing_links_by_page(self, page, use_drawings_tab=False):
        """Scrapes the links of all drawings at the given page made by this player.
        
        By default, we get drawing panels using the 'public games' tab.
        Drawception drawings created after 2021-12-17 are partially broken. Broken
        drawings do not appear in the 'Drawings' tab.
        """
        url = ""
        if use_drawings_tab:
            url = urllib.parse.urljoin(self.url,  "drawings/")
        else:
            url =  urllib.parse.urljoin(self.url, "games/")
        return DrawceptionPlayer.get_drawing_links_from_url(urllib.parse.urljoin(url, str(page) + '/'))

    def scrape_drawing_links(self, use_drawings_tab=False, max_pages=100):
        """Scrapes the links of all drawings up to the max_pages made by this player.
        
        By default, we get drawing panels using the 'public games' tab.
        Drawception drawings created after 2021-12-17 are partially broken. Broken
        drawings do not appear in the 'Drawings' tab.

        There also exists a bug in which we can bypass the 100 page limit by setting the
        page number to be negative. Page x and -x + 2 are the same.
        """
        for page in range(1, max_pages + 1):
            if page > 100:
                page = -page + 2
            new_links = self.scrape_drawing_links_by_page(page, use_drawings_tab)
            if new_links == None:
                break
            self.drawings.union(new_links)
            time.sleep(2)
        return self.drawings

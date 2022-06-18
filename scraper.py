import requests
import urllib.request
from bs4 import BeautifulSoup

def get_panel_svg(sessionid, panelid):
    """Gets the svg from drawception, given the panel id.

    Getting svg images requires a session cookie for images created before
    2021-12-17.
    """
    url = "https://stage.drawception.com/panel/getsvg.json" # TODO: Enable choice between test and drawception
    cookie = {"PHPSESSID": sessionid}
    request = {'panelid': panelid}
    page = requests.post(url, json=request, cookies=cookie)
    if page.status_code != 200:
        return ""
    else:
        return page.text

def download_panel(panelid, folder="./images/"):
    """Downloads the panel image from drawception, given the panel id and saves
    it into the specified folder.

    Drawception drawings created after 2021-12-17 are partially broken. Png's fail to load
    due to an access denied bug. It is only possible to download svg images.
    """
    url = "https://drawception.com/panel/drawing/" + panelid + "/1/" # TODO: Enable choice between test and drawception
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    image = soup.find_all('img', class_="gamepanel-minsize gamepanel-shadow img-responsive")[0]
    src = image['src']
    name = image['alt']
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
    urllib.request.install_opener(opener)
    if "http" in src:
        urllib.request.urlretrieve(src, folder + panelid + "_" + name + ".png")
    else:
        urllib.request.urlretrieve(src, folder + panelid + "_" + name + ".svg")
    

if __name__ == "__main__":
    
    session_f = open("sessionid", 'r')
    sessionid = session_f.readline()
    session_f.close()
    panelid = "1234567890"
    download_panel(panelid)
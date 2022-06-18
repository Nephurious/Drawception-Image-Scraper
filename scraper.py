import requests
from bs4 import BeautifulSoup

def get_panel_svg(sessionid, panelid):
    """Gets the svg from drawception, given the panel id.

    Getting svg images requires a session cookie.
    """
    url = "https://stage.drawception.com/panel/getsvg.json"
    cookie = {"PHPSESSID": sessionid}
    request = {'panelid': panelid}
    page = requests.post(url, json=request, cookies=cookie)
    if page.status_code != 200:
        return ""
    else:
        return page.text

if __name__ == "__main__":
    
    session_f = open("sessionid", 'r')
    sessionid = session_f.readline()
    session_f.close()
    panelid = "1234567890"
    print(get_panel_svg(sessionid, panelid))

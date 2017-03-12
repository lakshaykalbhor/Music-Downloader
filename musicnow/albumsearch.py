"""
Return Album Art url
"""

import json
import requests
import six
import spotipy

from os.path import realpath, basename

if six.PY2:
    import BeautifulSoup
    from urllib2 import quote, Request, urlopen
elif six.PY3:
    from bs4 import BeautifulSoup
    from urllib.parse import quote
    from urllib.request import Request, urlopen

# Project specific inputs
import log
from utils import *

def img_bing(album):
    """
    Bing image search
    """

    setup()

    log.log_indented('* Trying to extract album art from Bing')

    album += " Album Art"

    api_key = "Key"
    endpoint = "https://api.cognitive.microsoft.com/bing/v5.0/images/search"
    links_dict = {}

    headers = {'Ocp-Apim-Subscription-Key': str(BING_KEY)}
    param = {'q': album, 'count': '1'}

    response = requests.get(endpoint, headers=headers, params=param)
    response = response.json()

    key = 0
    try:
        for i in response['value']:
            links_dict[str(key)] = str((i['contentUrl']))
            key = key + 1

        return links_dict["0"]

    except KeyError:
        return None

def img_google(album):
    """
    Google image search
    """

    log.log_indented('* Trying to extract album art from Google')

    album += " Album Art"
    url = ("https://www.google.com/search?q=" +
           quote(album.encode('utf-8')) + "&source=lnms&tbm=isch")
    header = {'User-Agent':
              '''Mozilla/5.0 (Windows NT 6.1; WOW64)
              AppleWebKit/537.36 (KHTML,like Gecko)
              Chrome/43.0.2357.134 Safari/537.36'''
             }

    soup = BeautifulSoup(urlopen(Request(url, headers=header)), "html.parser")

    albumart_div = soup.find("div", {"class": "rg_meta"})
    albumart = json.loads(albumart_div.text)["ou"]

    return albumart

def img_spotify(query):
    log.log_indented('* Trying to extract album art from Spotify')
    spotify = spotipy.Spotify()

    album = spotify.search(q='album:' + query, limit=1)
    return album['tracks']['items'][0]['album']['images'][0]['url']

def img_search(query):
    return img_spotify(query) or img_google(query) or img_bing(query)


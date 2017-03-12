#!/usr/bin/env python

r"""
  __  __           _      _   _               
 |  \/  |_   _ ___(_) ___| \ | | _____      __
 | |\/| | | | / __| |/ __|  \| |/ _ \ \ /\ / /
 | |  | | |_| \__ \ | (__| |\  | (_) \ V  V / 
 |_|  |_|\__,_|___/_|\___|_| \_|\___/ \_/\_/  
                                              
"""

import argparse
import requests
import six
import spotipy
import youtube_dl

from os import name, system
from os.path import exists
from collections import OrderedDict

if six.PY2:
    import BeautifulSoup
    input = raw_input
elif six.PY3:
    from bs4 import BeautifulSoup

# Project specific inputs
import repair
import log
from utils import *

YOUTUBECLASS = 'spf-prefetch'
clear = 'clear' if name != 'nt' else 'cls'


def add_config():
    """
    Prompts user for API keys, adds them in an .ini file stored in the same
    location as that of the script
    """

    genius_key = input('Enter Genius key : ')
    bing_key = input('Enter Bing key : ')

    CONFIG['keys']['bing_key'] = bing_key
    CONFIG['keys']['genius_key'] = genius_key

    with open(config_path, 'w') as configfile:
        CONFIG.write(configfile)


def get_tracks_from_album(album_name):
    """
    Gets tracks from an album using Spotify's API
    """

    spotify = spotipy.Spotify()

    result = spotify.search(q='album:' + album_name, limit=1)
    result = result['tracks']['items'][0]['album']
    album, album_id, artist = result['name'], result['id'], result['artists'][0]['name']
    result = spotify.album_tracks(album_id=album_id)
    songs = [item['name'] for item in result['items']]
    return songs, album, artist


def get_url(song_input, auto):
    """
    Provides user with a list of songs to choose from
    returns the url of chosen song.
    """

    youtube_list = OrderedDict()
    num = 0  # List of songs index

    html = requests.get('https://www.youtube.com/results',
                        params={'search_query': song_input})
    soup = BeautifulSoup(html.text, 'html.parser')

    # In all Youtube Search Results
    for i in soup.findAll('a', {'rel': YOUTUBECLASS}):
        song_url = 'https://www.youtube.com' + (i.get('href'))
        song_title = i.get('title')
        # Add title and song url to dictionary
        youtube_list.update({song_title: song_url})

        if auto:
            print(song_title)
            return list(youtube_list.values())[0], list(youtube_list.keys())[0]

        num += 1
        print("({0}) {1}".format(num, song_title))  # Prints list

    if not youtube_list:
        log.log_error('No match found on YouTube, try refining your search!')
        exit()

    # Gets and returns the demanded song url and title and url
    return prompt(youtube_list)


def prompt(youtube_list):
    """
    Prompts for song number from list of songs
    """

    option = 0
    while not option:
        try:
            option = int(input('\nEnter song number > '))
        except ValueError:
            print('Value entered not a number. Try again.')

    try:
        song_url = list(youtube_list.values())[option - 1]
        song_title = list(youtube_list.keys())[option - 1]
    except IndexError:
        log.log_error('Invalid Input')
        exit()

    system(clear)
    print('Download Song: ')
    print(song_title)
    print('Y/N?')
    confirm = input('> ')
    if not confirm or confirm.lower() == 'y':
        pass
    elif confirm.lower() == 'n':
        exit()
    else:
        log.log_error('Invalid Input')
        exit()

    return song_url, song_title


def download_song(song_url, song_title):
    """
    Downloads song from youtube-dl
    """
    outtmpl = song_title + '.%(ext)s'
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        },
            {'key': 'FFmpegMetadata'},
        ],

    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song_url, download=True)


def music_now(query, auto):
    """
    Finds the YouTube URL of the queried song, downloads
    it as MP3 file and adds the appropriate tags.
    """

    song_url, file_name = get_url(query, auto)
    download_song(song_url, file_name)
    system(clear)
    repair.fix_music(file_name + '.mp3')


def main():
    """
    Starts here, handles arguments
    """

    global clear

    parser = argparse.ArgumentParser(
        description='Download songs with album art and metadata!')
    parser.add_argument('-c', '--config', action='store_true',
                        help='Set your API keys')
    parser.add_argument('-m', '--multiple', action='store', dest='multiple_file',
                        help='Download multiple songs from a text file list. \
                        Tip: write song and artist in the same line')
    parser.add_argument('-a', '--auto', action='store_true',
                        help='Automatically chooses top result')
    parser.add_argument('--album', action='store_true',
                        help='Downloads all songs from an album')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Activate verbose output (no console clears)')
    args = parser.parse_args()
    arg_multiple = args.multiple_file or None
    arg_auto = args.auto or None
    arg_album = args.album or None
    arg_config = args.config
    clear = '' if args.verbose else clear

    system(clear)

    setup()

    if arg_config:
        add_config()

    elif arg_multiple and arg_album:
        log.log_error('Incompatible options "multiple" and "album!"')

    elif arg_album:
        album_name = input('Enter album information (name and artist): ')
        try:
            tracks, album, artist = get_tracks_from_album(album_name)
            print("\nArtist: {}\nAlbum: {}\nSongs:\n\t{}".format(
                  artist, album, '\n\t'.join(tracks)))
            confirm = input(
                '\nAre these the songs you want to download? (Y/N)\n> ')

        except IndexError:
            log.log_error('Couldn\'t find album')
            exit()

        if not confirm or confirm.lower() == ('y'):
            for track_name in tracks:
                music_now("{} {}".format(track_name, artist), arg_auto)

        elif confirm.lower() == 'n':
            log.log_error('Sorry if appropriate results weren\'t found.' \
                          'Try adding more album information such as artist.')
            exit()
        else:
            log.log_error('Invalid Input')
            exit()

    elif arg_multiple:
        if not exists(arg_multiple):
            log.log_error('Requested file for multiple download "{}" ' \
                          'not found'.format(arg_multiple))
            exit()

        with open(arg_multiple, 'r') as f:
            file_names = [line.strip() for line in f if line.strip()]

        for files in file_names:
            music_now(files, arg_auto)

    else:
        query = input('Enter Song Information: ')
        music_now(query, arg_auto)


if __name__ == '__main__':
    main()


#!/usr/bin/env python

from . import repair
from . import log

import sys
import argparse
from os import system, rename, listdir, curdir, name
from os.path import basename
from collections import OrderedDict
import re

from bs4 import BeautifulSoup
import requests
import youtube_dl

import six

if six.PY2:
    from urllib2 import urlopen
    from urllib2 import quote
    input = raw_input
elif six.PY3:
    from urllib.parse import quote
    from urllib.request import urlopen

YOUTUBECLASS = 'spf-prefetch'


def get_url(song_input, auto):

    print('\n')

    youtube_list = OrderedDict()
    num = 0  # List of songs index

    html = requests.get("https://www.youtube.com/results",params={'search_query':song_input})
    soup = BeautifulSoup(html.text, 'html.parser')

    # In all Youtube Search Results

    for i in soup.findAll('a', {'rel': YOUTUBECLASS}):
        song_url = 'https://www.youtube.com' + (i.get('href'))
        song_title = (i.get('title'))
        # Adds title and song url to dictionary
        youtube_list.update({song_title: song_url})

        if not auto:
            print('(%s) %s' % (str(num + 1), song_title))  # Prints list
            num = num + 1

        elif auto:
        	print(song_title)
        	return list(youtube_list.values())[0], list(youtube_list.keys())[0]

    # Checks if YouTube search return no results
    if youtube_list == {}:
        print("No match found!")
        sys.exit()

    # Gets the demanded song title and url
    song_url, song_title = prompt(youtube_list)

    return song_url, song_title  # Returns Name of Song and URL of Music Video



def prompt(youtube_list):

    while True:
        option = int(input('\nEnter song number > '))
        try:
            song_url = list(youtube_list.values())[option - 1]
            song_title = list(youtube_list.keys())[option - 1]
            break
        except IndexError:
            pass

    system('clear')
    print('Download Song: ')
    print(song_title)
    print('Y/N?')
    confirm = input('>')
    if confirm == 'Y' or confirm == 'y':
        pass
    elif confirm == 'N' or confirm == 'n':
        exit()
    else:
        log.log_error('Invalid Input')
        exit()

    return song_url, song_title


def download_song(song_url, song_title):

    file_name = None

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([song_url])  # Downloads audio using youtube-dl

    try:

        files = listdir(curdir)
        for songs in files:
            re_found = re.match(re.escape(song_title) +
                                r'.*\.mp3$', songs, re.UNICODE)
            if re_found:
                file_name = re_found.group()
                break

        if file_name != None:
            # Renames file to song title
            rename(file_name, song_title + '.mp3')
        else:
            file_name = (song_title + '-' + song_url[32:] + '.mp3')
            rename(file_name, song_title + '.mp3')
    except Exception:
        log.log_error("Could not rename the file")
        pass


def main():
    system('clear')

    parser = argparse.ArgumentParser(description='Download songs with album art and metadata!')
    parser.add_argument('-m', '--multiple', action='store', dest='multiple_file', help='Download multiple songs from a text file list')
    parser.add_argument('-a', '--auto', action='store_true', help='Automatically chooses top result')
    args = parser.parse_args()
    arg_multiple = args.multiple_file or None
    arg_auto = args.auto or None

    if arg_multiple:
    	with open(arg_multiple, "r") as f:
    		file_names = []
    		for line in f:
    			file_names.append(line.rstrip('\n'))

    	for files in file_names:
    		song_url, file_name = get_url(files, arg_auto)
    		download_song(song_url, file_name)
    		system('clear')
    		repair.fix_music(file_name + '.mp3')


    else:
        query = input('Enter Song Name : ')
        song_url, file_name = get_url(query, arg_auto)  # Gets YT url
        download_song(song_url, file_name)  # Saves as .mp3 file
        system('clear')
        repair.fix_music(file_name + '.mp3')


if __name__ == '__main__':
    main()

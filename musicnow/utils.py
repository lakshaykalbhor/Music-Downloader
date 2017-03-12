#!/usr/bin/env python

import six
from os.path import basename, realpath

if six.PY2:
    import ConfigParser as configparser
elif six.PY3:
    import configparser

CONFIG = ''
BING_KEY = ''
GENIUS_KEY = ''
config_path = ''
LOG_FILENAME = 'musicrepair_log.txt'
LOG_LINE_SEPARATOR = '........................\n'

def setup():
    """
    Gathers all configs
    """

    global CONFIG, BING_KEY, GENIUS_KEY, config_path, LOG_FILENAME, LOG_LINE_SEPARATOR


    CONFIG = configparser.ConfigParser()
    config_path = realpath(__file__).replace(basename(__file__), 'config.ini')
    CONFIG.read(config_path)

    GENIUS_KEY = CONFIG['keys']['genius_key']
    BING_KEY = CONFIG['keys']['bing_key']

    if GENIUS_KEY == '<insert genius key here>':
        log.log_warn('Warning, you are missing the Genius key. Add it using --config')

    if BING_KEY == '<insert bing key here>':
        log.log_warn('Warning, you are missing the Bing key. Add it using --config')


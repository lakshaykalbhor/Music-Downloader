#!/usr/bin/env python

from colorama import Fore

# Project specific inputs
from utils import *

setup()

def log(text='', newline=False, trailing_newline=False):
    newline_char = ''
    trailing_newline_char = ''
    if newline:
        newline_char = '\n'
    if trailing_newline:
        trailing_newline_char = '\n'
    print('%s%s%s' % (newline_char, text, trailing_newline_char))


def log_indented(text='', newline=False, trailing_newline=False):
    log('    %s' % text, newline=newline, trailing_newline=trailing_newline)


def log_error(text='', indented=False):
    msg = '%s%s%s' % (Fore.RED, text, Fore.RESET)
    if indented:
        log_indented(msg)
    else:
        log(msg)


def log_warn(text='', indented=False):
    msg = '%s%s%s' % (Fore.YELLOW, text, Fore.RESET)
    if indented:
        log_indented(msg)
    else:
        log(msg)


def log_success():
    log(LOG_LINE_SEPARATOR)
    text = 'Finished successfully'
    log('%s%s%s' % (Fore.GREEN, text, Fore.RESET))

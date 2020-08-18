import re

from labirinth.settings import LOW_EXTENSION, MEDIUM_EXTENSION, HEIGHT_EXTENSION


START_CONV_TEXT = 'GO'

NUMBER = re.compile('^[0-9]+$')
START_CONV = re.compile(f'^{START_CONV_TEXT}$')
EXTENSION = re.compile(f'^{LOW_EXTENSION}|{MEDIUM_EXTENSION}|{HEIGHT_EXTENSION}$')

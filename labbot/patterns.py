import re


START_CONV_TEXT = 'GO'

NUMBER = re.compile('^[0-9]+$')
START_CONV_PATTERN = re.compile(f'^{START_CONV_TEXT}$')

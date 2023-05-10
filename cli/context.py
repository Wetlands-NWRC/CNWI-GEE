import os
import sys


""" 
adds the cwni module to the python path, makes it importable
"""

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

MODULE_PATH = os.path.join(CURRENT_DIR, '..', 'cnwi')

sys.path.insert(0, MODULE_PATH)

import cnwi
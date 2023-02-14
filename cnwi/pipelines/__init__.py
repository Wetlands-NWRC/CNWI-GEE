import os
import sys

import ee

if not ee.data._credentials:
    ee.Initialize()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
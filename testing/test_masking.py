import os
import sys

import ee

ee.Initialize()
current_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(current_dir)
sys.path.insert(0, "../")

from cnwi import masking
from cnwi.datasets import dem

IMAGE = ee.Image("users/ryangilberthamilton/BC/williston/stacks/WillistonA_2018")


def test_slope_mask():
    de = dem.NASADEM_HGT().select('elevation')
    slope = ee.Terrain.slope(de)
    mask = masking.slope_mask(de, deg=15)
    masked = mask(IMAGE)
    masked.getInfo()
    return None

if __name__ == '__main__':
    test_slope_mask()
import os
import sys

import ee

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

os.chdir(CURRENT_DIR)
sys.path.insert(0, "../")

from cnwi import inputs
from cnwi.datasets import dem
from cnwi.eelib import eefuncs

TARGET_AREA = ee.FeatureCollection("users/ryangilberthamilton/BC/williston/williston_sub_a_2019")


def test_dem_inputs():
    rectangle = eefuncs.create_rectangle(TARGET_AREA)
    
    dem_inputs = inputs.DEMInputs(
        ee_image=dem.NASADEM_HGT().select('elevation'),
        rectangle=rectangle
    )

def test_dem_export():
    # defaults
    rectangle = eefuncs.create_rectangle(TARGET_AREA)
    
    dem_inputs = inputs.DEMInputs(
        ee_image=dem.NASADEM_HGT().select('elevation'),
        rectangle=rectangle
    )
    
    export_image = ee.Image.cat(*dem_inputs.products)
    
    ee.batch.Export.image.toDrive(
        image=export_image,
        folder='DEM_TESTING',
        description="DEM_TA_TEST_1",
        maxPixels=1e13,
        region=rectangle
    ).start()


if __name__ == '__main__':
    ee.Initialize()
    test_dem_export()
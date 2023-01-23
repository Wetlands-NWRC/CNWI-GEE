import os

import ee
import eelib
from dotenv import load_dotenv
from pipelines import eerfpl, factories, colors

load_dotenv()


def datacube():
    pass

def benchmark():
    pass

def datacube_lsc():
    viewport = ee.FeatureCollection.from_file(
        filename = "../000-data/viewport.shp"
    ).geometry()

    training_data = ee.FeatureCollection.from_file(
        filename="../../phase01/000-data/training_data.gdb",
        driver='FileGDB',
        layer='training_points_700'
    )

    with open("../data/systems.txt", 'r') as file:
        ids = [line.strip() for line in file.readlines()]

    ee_images = [ee.Image(f'COPERNICUS/S1_GRD/{_}') for _ in ids]

    datacube = factories.DatacubeCollection(
        arg="projects/fpca-336015/assets/williston-cba"
    ).filterBounds(viewport)

    s1_collection = ee.ImageCollection(ee_images)

    dem = ee.Image("NASA/NASADEM_HGT/001").select('elevation')

    pipeline = eerfpl.DataCubePipelineLSC(
    sar=s1_collection,
    optical=datacube,
    dem=dem,
    training_data=training_data
)

    # Export Settings
    pipeline.bucket = os.environ.get('BUCKET')
    pipeline.root = os.environ.get('ROOT')
    pipeline.caseNumber = "Phase02"
    pipeline.region = viewport

    output = pipeline.run()

    pipeline.logging()

    pipeline.exportToCloud()

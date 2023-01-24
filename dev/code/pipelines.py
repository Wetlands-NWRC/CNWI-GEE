import os

from typing import Dict, Any

import ee
import eelib
import yaml

from dotenv import load_dotenv
from pipelines import eerfpl, factories

load_dotenv()


def datacube():
    pass

def benchmark(cfg_filename: str):
    with open(cfg_filename) as stream:
            CFG: Dict[str, Any] = yaml.safe_load(stream=stream)

    cfg_viewport = CFG['viewport']
    viewport = ee.FeatureCollection.from_file(
        filename=cfg_viewport.get('file_name'),
        driver=cfg_viewport.get('driver')
    ).geometry()

    cfg_training_data = CFG['training_data']
    training_data = ee.FeatureCollection.from_file(
        filename=cfg_training_data.get('file_name'),
        driver=cfg_training_data.get('driver', None),
        layer=cfg_training_data.get('layer', None)
    )

    s1_imgs = factories.s1_factory(
        asset_ids=CFG['assets']['benchmark']['S1']
    )

    s2_imgs = factories.s2_factory(
        asset_ids=CFG['assets']['benchmark']['S2']
    )

    dem = ee.Image(CFG['assets']['dem']).select('elevation')

    pipeline = eerfpl.BenchmarkPipeline(
        sar=s1_imgs,
        optical=s2_imgs,
        dem=dem,
        training_data=training_data
    )

    # Export Settings
    pipeline.bucket = os.environ.get('BUCKET')
    pipeline.root = os.environ.get('ROOT')
    pipeline.caseNumber = CFG['phase']
    pipeline.region = viewport

    pipeline.run()

    pipeline.logging()

    pipeline.exportToCloud()

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

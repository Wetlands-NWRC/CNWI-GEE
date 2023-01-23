import os

import ee
import eelib
import factory
import yaml
from dotenv import load_dotenv
from eelib.scripttools import eemoa

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def main():
    BUCKET = os.environ.get('BUCKET')

    with open("./config.yaml") as stream:
        CFG = yaml.safe_load(stream)

    viewport_cfg = CFG.get('viewport')
    training_data_cfg = CFG.get('training_data')
    dc_assets_cfg = CFG.get('datacube')

    viewport = ee.FeatureCollection.from_file(
        filename=viewport_cfg.get('file_name'),
        driver=viewport_cfg.get('driver')
    ).geometry()

    s1_imgs = factory.s1_factory(dc_assets_cfg.get('S1'))
    dc_imgs = factory.datacube_factory(
        asset_id=dc_assets_cfg.get('S2').get('DC'),
        viewport=viewport
    )

    stack = ee.Image.cat(*s1_imgs, *dc_imgs)

    training_data = factory.training_data(
        file_name=training_data_cfg.get('file_name'),
        driver=training_data_cfg.get('driver', None),
        layer=training_data_cfg.get('layer', None)
    )

    moa_table = eemoa(
        image=stack,
        label_col='land_cover',
        pts=training_data
    )

    task: ee.batch.Task = ee.batch.Export.table.toCloudStorage(
        collection=moa_table,
        description='datacube_moa_scores',
        bucket=BUCKET,
        fileNamePrefix='development/phase01/datacube/moa-datacube',
        fileFormat='CSV'
    )

    task.start()


if __name__ == "__main__":
    os.chdir(CURRENT_DIR)
    load_dotenv()
    main()

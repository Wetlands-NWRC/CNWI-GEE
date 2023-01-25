import os
from typing import Any, Dict

import ee
import yaml
from dotenv import load_dotenv
from pipelines import eerfpl, factories

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    with open("./config.yaml") as stream:
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


if __name__ == "__main__":
    os.chdir(CURRENT_DIR)
    load_dotenv()
    main()

import os

import ee
import eelib
import yaml
from dotenv import load_dotenv
from eelib import eefuncs, sf
from eelib.scripttools import eemoa
from pipelines import factories

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))


def main():
    BUCKET = os.environ.get('BUCKET')

    with open("./config.yaml") as stream:
        CFG = yaml.safe_load(stream)

    cfg_viewport = CFG['viewport']
    viewport = ee.FeatureCollection.from_file(
        filename=cfg_viewport.get('file_name'),
        driver=cfg_viewport.get('driver')
    ).geometry()

    s1_imgs = factories.s1_factory(
        asset_ids=CFG['assets']['datacube']['S1']
    )

    s1_pre_1 = eefuncs.batch_co_register(s1_imgs, 1)
    s1_pre_2 = eefuncs.batch_despeckle(s1_pre_1, sf.Boxcar(1))

    ratios = eefuncs.batch_create_ratio(s1_pre_2, 'VV', 'VH')

    datacube = factories.DatacubeCollection(
        arg=CFG['assets']['datacube']['S2']['DC']
    )

    dc_imgs = factories.datacube_img_factory(
        datacube_collection=datacube,
        viewport=viewport
    )

    savis = eefuncs.batch_create_savi(dc_imgs)
    ndvis = eefuncs.batch_create_ndvi(dc_imgs)
    tassels = eefuncs.batch_create_tassel_cap(dc_imgs)

    dem = ee.Image(CFG['assets']['dem']).select('elevation')

    slope = ee.Terrain.slope(dem)

    stack = ee.Image.cat(*s1_pre_2, *ratios, *dc_imgs, *savis, *ndvis, *tassels,
                         dem, slope)

    cfg_training_data = CFG['training_data']
    training_data = ee.FeatureCollection.from_file(
        filename=cfg_training_data.get('file_name'),
        driver=cfg_training_data.get('driver', None),
        layer=cfg_training_data.get('layer', None)
    )

    samples = stack.sampleRegions(
        collection=training_data,
        tileScale=16,
        scale=10
    )
    
    # moa_table = eemoa(
    #     image=stack,
    #     label_col='land_cover',
    #     pts=training_data
    # )

    task: ee.batch.Task = ee.batch.Export.table.toCloudStorage(
        collection=samples,
        description='samples',
        bucket=BUCKET,
        fileNamePrefix='{root}/{phase}/datacube/moa-datacube'.format(
            root=os.environ.get('ROOT'), phase=CFG['phase']),
        fileFormat='CSV'
    )

    task.start()


if __name__ == "__main__":
    os.chdir(CURRENT_DIR)
    load_dotenv()
    main()

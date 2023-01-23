import os
from typing import Any, Dict

import ee
import factory
import yaml
from dotenv import load_dotenv
from eelib import bands, classifiers, eefuncs, sf, td
from pipelines import colors, eerfpl, logging

load_dotenv()


def datacube(config):

    with open(config) as stream:
        CFG: Dict[str, Any] = yaml.safe_load(stream=stream)

    viewport_cfg = CFG.get('viewport', None)
    training_data_cfg = CFG.get('training_data', None)
    model_cfg = CFG.get('model_config', None)
    assets_cfg = CFG.get('assets')
    dc_cfg = assets_cfg.get('datacube')
    dem_cfg = assets_cfg.get('dem')

    viewport = ee.FeatureCollection.from_file(
        filename=viewport_cfg.get('file_name'),
        driver=viewport_cfg.get('driver')
    ).geometry()

    training_data = factory.training_data(
        file_name=training_data_cfg.get('file_name'),
        driver=training_data_cfg.get('driver', None),
        layer=training_data_cfg.get('layer', None)
    )

    # Sentinel - 1
    s1_imgs = factory.s1_factory(dc_cfg.get('S1'))
    s1_imgs = eefuncs.batch_co_register(s1_imgs, max_offset=10)
    s1_imgs = eefuncs.batch_despeckle(
        s1_imgs, sf.Boxcar(1)
    )

    s1_drivs = eefuncs.batch_create_ratio(s1_imgs, 'VV', 'VH')

    # Sentinel - 2
    dc_imgs = factory.datacube_factory(
        asset_id=dc_cfg.get('S2').get('DC'),
        viewport=viewport
    )

    s2_drivs = [
        *eefuncs.batch_create_ndvi(dc_imgs),
        *eefuncs.batch_create_savi(dc_imgs),
        *eefuncs.batch_create_tassel_cap(dc_imgs)
    ]

    # DEM
    # dem = ee.Image(dem_cfg).select('elevation')

    # Stack
    stack = ee.Image.cat(*dc_imgs, *s1_imgs, *s2_drivs, *s1_drivs)

    # Create Training Data obj
    training_data = td.TrainingData(
        collection=training_data
    )

    # Sample the Training Data Obj against training_data
    td.training_samples(
        image=stack,
        training_data=training_data,
        scale=10,
        tile_scale=16
    )

    sampled = training_data.samples
    sampled = eefuncs.new_labels(sampled, labelcol='land_values', offset=1)
    labels = training_data.collection.aggregate_array('land_cover').distinct()
    # classifier
    model = classifiers.RandomForest(
        n_trees=10
    )

    model.train(
        featues=sampled,
        class_label='land_values',
        predictors=stack.bandNames()
    )

    classify = stack.classify(model.model)
    cfm = model.confusion_matrix(
        labels=labels
    )

    ############################################################################
    # Logging
    ############################################################################
    logger = logging.eeLogger

    # logging
    # Data Cube logging
    # dc_tiles = logger.dct_logger(
    #     tileIDs=dc_imgs[1].aggregate_array('tileID'),
    #     system_index=dc_imgs[1].aggregate_array('system:index')
    # )
    # # dc_dates = logger.datacube_dates()

    # # Sentiel - 1 Logging
    # s1_log = logger.Sentinel1_Logger(s1_imgs)

    # # Training Data logging
    # training_data = output.get('training_data')

    # lookup = logger.lookup(
    #     collection=training_data.collection,
    #     label_col=training_data.class_labels,
    #     value_col=training_data.class_values,
    #     colors=colors.Colors.to_eeDict()
    # )

    # log_predictors = logger.predictors(pipe.predictors)

    ############################################################################
    # Exports
    ############################################################################

    BUCKET = os.environ.get('BUCKET')
    ROOT = os.environ.get('ROOT')
    PHASE = CFG.get('phase')

    dest = "{root}/{phase}/datacube/{filename}"

    # dct_task = ee.batch.Export.table.toCloudStorage(
    #     collection=dc_tiles,
    #     description='data-cube-tiles',
    #     bucket=BUCKET,
    #     fileNamePrefix=dest.format(
    #         root=ROOT, phase=PHASE, filename="datacube-tileids"),
    #     fileFormat='CSV'
    # )

    # dc_dates_task = ee.batch.Export.table.toCloudStorage(
    #     collection=dc_dates,
    #     description='data-cube-dates',
    #     bucket=BUCKET,
    #     fileNamePrefix=dest.format(
    #         root=ROOT, phase=PHASE, filename="datacube-dates"),
    #     fileFormat='CSV'
    # )

    # dc_s1_task = ee.batch.Export.table.toCloudStorage(
    #     collection=s1_log,
    #     description='data-cube-s1',
    #     bucket=BUCKET,
    #     fileNamePrefix=dest.format(
    #         root=ROOT, phase=PHASE, filename="datacube-s1-log"),
    #     fileFormat='CSV'
    # )

    # dc_lookup_task = ee.batch.Export.table.toCloudStorage(
    #     collection=lookup,
    #     description='data-cube-lookup',
    #     bucket=BUCKET,
    #     fileNamePrefix=dest.format(
    #         root=ROOT, phase=PHASE, filename="datacube-lookup"),
    #     fileFormat='CSV'
    # )

    # predic_task = ee.batch.Export.table.toCloudStorage(
    #     collection=log_predictors,
    #     description='data-cube-predictors',
    #     bucket=BUCKET,
    #     fileNamePrefix=dest.format(
    #         root=ROOT, phase=PHASE, filename="datacube-predictors"),
    #     fileFormat='CSV'
    # )

    sub_dest = "{root}/{phase}/datacube/{child}/{filename}"
    # # Training Data

    # td_o = output.get('training_data')

    # dc_td_task = ee.batch.Export.table.toCloudStorage(
    #     collection=td_o.collection,
    #     description='data-cube-training-data',
    #     bucket=BUCKET,
    #     fileNamePrefix=sub_dest.format(
    #         root=ROOT, phase=PHASE, child="training_data",
    #         filename="datacube_training_data"),
    #     fileFormat='SHP'
    # )

    # # Samples
    # dc_sm_task = ee.batch.Export.table.toCloudStorage(
    #     collection=td_o.samples,
    #     description='data-cube-training-data-samples',
    #     bucket=BUCKET,
    #     fileNamePrefix=sub_dest.format(
    #         root=ROOT, phase=PHASE, child="training_data",
    #         filename="datacube_training_samples"),
    #     fileFormat='SHP'
    # )

    # confusion matrix
    dc_cm_task = ee.batch.Export.table.toCloudStorage(
        collection=cfm,
        description='data-cube-confusion-matrix',
        bucket=BUCKET,
        fileNamePrefix=dest.format(
            root=ROOT, phase=PHASE,
            filename="datacube-confusion-matrix"),
        fileFormat='CSV'
    )

    # classification
    dc_cly_task = ee.batch.Export.image.toCloudStorage(
        image=classify,
        description='data-cube-classification',
        bucket=BUCKET,
        fileNamePrefix=sub_dest.format(root=ROOT, phase=PHASE,
                                       child='classification',
                                       filename='datacube-classification'),
        region=viewport,
        scale=10,
        crs="EPSG:4326",
        maxPixels=1e13,
        shardSize=1000,
        fileDimensions=[1000, 1000],
        fileFormat='GeoTIFF',
    )

    tasks = [dc_cm_task, dc_cly_task]

    [task.start() for task in tasks]


def benchmark(config):

    with open(config) as stream:
        CFG: Dict[str, Any] = yaml.safe_load(stream=stream)

    viewport_cfg = CFG.get('viewport', None)
    training_data_cfg = CFG.get('training_data', None)
    model_cfg = CFG.get('model_config', None)
    assets_cfg = CFG.get('assets')
    bm_cfg = assets_cfg.get('benchmark')
    dem_cfg = assets_cfg.get('dem')

    viewport = ee.FeatureCollection.from_file(
        filename=viewport_cfg.get('file_name'),
        driver=viewport_cfg.get('driver')
    ).geometry()

    training_data = ee.FeatureCollection.from_file(
        filename=training_data_cfg.get('file_name'),
        driver=training_data_cfg.get('driver', None),
        layer=training_data_cfg.get('layer', None)
    )

    # Sentinel - 1
    s1_const = bm_cfg.get('S1')
    s1_imgs = factory.s1_factory(s1_const)
    s1_imgs = eefuncs.batch_co_register(s1_imgs, max_offset=10)
    s1_imgs = eefuncs.batch_despeckle(
        s1_imgs, sf.Boxcar(1)
    )

    s1_drivs = eefuncs.batch_create_ratio(s1_imgs, 'VV', 'VH')

    # Sentinel - 2
    s2_imgs = factory.s2_factory(bm_cfg.get('S2'))

    s2_drivs = [
        *eefuncs.batch_create_ndvi(s2_imgs),
        *eefuncs.batch_create_savi(s2_imgs),
        *eefuncs.batch_create_tassel_cap(s2_imgs)
    ]

    # DEM
    dem = ee.Image(dem_cfg).select('elevation')

    # Stack
    stack = ee.Image.cat(*s2_imgs, *s1_imgs, *s2_drivs, *s1_drivs)

    # Sample the Training Data Obj against training_data
    sampled = stack.sampleRegions(**{
        'collection': training_data,
        'scale': 10,
        'tileScale': 8
    })

    sampled = eefuncs.new_labels(sampled, labelcol='land_values', offset=1)
    labels = training_data.aggregate_array('land_cover').distinct()
    # classifier
    model = classifiers.RandomForest(
        n_trees=1000
    )

    model.train(
        featues=sampled,
        class_label='land_values',
        predictors=stack.bandNames()
    )

    classify = stack.classify(model.model)
    cfm = model.confusion_matrix(
        labels=labels
    )

    BUCKET = os.environ.get('BUCKET')
    ROOT = os.environ.get('ROOT')
    PHASE = CFG.get('phase')

    dest = "{root}/{phase}/benchmark/{filename}"
    sub_dest = "{root}/{phase}/benchmark/{child}/{filename}"
# confusion matrix
    dc_cm_task = ee.batch.Export.table.toCloudStorage(
        collection=cfm,
        description='benchmark-confusion-matrix',
        bucket=BUCKET,
        fileNamePrefix=dest.format(
            root=ROOT, phase=PHASE,
            filename="benchmark-confusion-matrix"),
        fileFormat='CSV'
    )

    # classification
    dc_cly_task = ee.batch.Export.image.toCloudStorage(
        image=classify,
        description='benchmark-classification',
        bucket=BUCKET,
        fileNamePrefix=sub_dest.format(root=ROOT, phase=PHASE,
                                       child='classification',
                                       filename='benchmark-classification'),
        region=viewport,
        scale=10,
        crs="EPSG:4326",
        maxPixels=1e13,
        shardSize=100,
        fileDimensions=[1000, 1000],
        fileFormat='GeoTIFF',
    )

    tasks = [dc_cm_task, dc_cly_task]

    [task.start() for task in tasks]


def datacubeLSC():
    pass


def benchmarkLSC():
    pass

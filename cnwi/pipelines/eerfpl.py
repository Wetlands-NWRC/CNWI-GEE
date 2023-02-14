
from abc import ABC, abstractmethod
from pprint import pprint
from typing import Dict, List, Union

import ee
from eelib import bands, eefuncs, sf, td
from eelib.classifiers import RandomForest

from . import colors, factories, logging


class Pipeline(ABC):

    @abstractmethod
    def run():
        pass


class eeRFPipeline(Pipeline):
    def __init__(self, sar: List[ee.Image], optical: List[ee.Image],
                 dem: ee.Image, training_data: ee.FeatureCollection) -> None:
        ###############################
        ###        Inputs         #####
        self._sar = sar
        self._optical = optical
        self._dem = dem
        self._training_data = training_data

        # Pipeline Default Settings
        ##############################
        ####   Training Data   #######
        self.land_cover = 'land_cover'
        self._samples = None

        ##############################
        # Random Forest Model settings
        self.n_trees = 1000
        self.predictors = None

        ##############################
        # Cloud Export Settings
        self.root: str = None
        self.bucket: str = None
        self.caseNumber: str = None
        self.region: ee.Geometry = None
        # export paths
        self._parent_cloud_path = "{root}/{phase}/{type}/{filename}"
        self._child_cloud_path = "{root}/{phase}/{type}/{child}/{filename}"

        # Task Confids
        self._tasks_CFG: List[ee.batch.Task] = []

        # set pipeline type
        self._type = "pipeline"

    # getters and setters to Change the pipelines Default settings

    def run(self) -> None:
        s1_imgs = self._sar
        # S1 Pre processing
        s1_imgs_despk = eefuncs.batch_despeckle(s1_imgs, sf.Boxcar(1))
        s1_ratios = eefuncs.batch_create_ratio(s1_imgs_despk, 'VV', 'VH')
        self._sar = s1_imgs_despk

        # S2 Pre Processing
        s2_ndvis = eefuncs.batch_create_ndvi(self._optical)
        s2_savis = eefuncs.batch_create_savi(self._optical)
        s2_tassels = eefuncs.batch_create_tassel_cap(self._optical)

        # DEM
        dem = self._dem.select('elevation')
        slope = ee.Terrain.slope(dem)

        # Create input Stack
        # TODO create a property for stack, and add DEM and slope
        stack = ee.Image.cat(*s1_imgs_despk, *s1_ratios, *self._optical, *s2_ndvis,
                             *s2_savis, *s2_tassels, dem, slope)

        # Sample the Stack
        samples = stack.sampleRegions(**{
            'collection': self._training_data,
            'scale': 10,
            'tileScale': 16
        })

        samples = eefuncs.new_labels(samples, self.land_cover, offset=1)

        self.samples = samples.get('dataset')
        # RF Model setup
        self.predictors = stack.bandNames() if self.predictors is None \
            else self.predictors

        model = RandomForest(
            n_trees=self.n_trees
        )

        model.train(
            featues=samples.get('dataset'),
            class_label='land_value',
            predictors=self.predictors
        )

        classified = stack.classify(model.model)
        cfm = model.confusion_matrix(
            labels=self._training_data.aggregate_array(
                self.land_cover)
            .distinct()
        )
        # TODO find a way to create task configs for output from run(), and
        # logging
        # set task configs
        # Create the Task
        image_task = ee.batch.Export.image.toCloudStorage(
            image=classified.int(),
            description=f'{self._type}-Classified-Image-Task',
            bucket=self.bucket,
            fileNamePrefix=self._child_cloud_path.format(
                root=self.root, phase=self.caseNumber, type=self._type,
                child='classification', filename=f'{self._type}-classified'
            ),
            region=self.region,
            scale=10,
            crs='EPSG:4326',
            maxPixels=1e13,
            shardSize=1000,
            fileDimensions=[1000, 1000],
            fileFormat='GeoTIFF'
        )
        self._tasks_CFG.append(image_task)

        cfm_task = ee.batch.Export.table.toCloudStorage(
            collection=cfm,
            description=f'{self._type}-confusion-matrix',
            bucket=self.bucket,
            fileNamePrefix=self._parent_cloud_path.format(
                root=self.root, phase=self.caseNumber, type=self._type,
                filename=f'{self._type}-{self.caseNumber}-confusion-matrix'),
            fileFormat='CSV'
        )

        self._tasks_CFG.append(cfm_task)

        return {'model': model, 'image': classified, 'confusion Matrix': cfm,
                'training_data': self._training_data}

    def logging(self):
        logger = logging.eeLogger

        # logging

        # Sentiel - 1 Logging
        s1_log = logger.Sentinel1_Logger(self._sar)
        s1_log_task = ee.batch.Export.table.toCloudStorage(
            collection=s1_log,
            bucket=self.bucket,
            description=f'{self._type}-Sentinel-1-log',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-Sentinel-1-log',
                                                         child='logging')
        )
        self._tasks_CFG.append(s1_log_task)

        # Training Data logging
        training_data = self._training_data

        training_task = ee.batch.Export.table.toCloudStorage(
            collection=training_data,
            bucket=self.bucket,
            description=f'{self._type}-training-data',
            fileFormat='SHP',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-training-data',
                                                         child='training-data')
        )
        self._tasks_CFG.append(training_task)

        lookup = logger.lookup(
            collection=self._samples,
            label_col=self.land_cover,
            value_col='land_value',
            colors=colors.Colors.to_eeDict()
        )
        look_log_task = ee.batch.Export.table.toCloudStorage(
            collection=lookup,
            bucket=self.bucket,
            description=f'{self._type}-lookup',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-training-data-lookup',
                                                         child='training-data')
        )
        self._tasks_CFG.append(look_log_task)

        log_predictors = logger.predictors(self.predictors)
        predic_log_task = ee.batch.Export.table.toCloudStorage(
            collection=log_predictors,
            bucket=self.bucket,
            description=f'{self._type}-predictors',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-predictors',
                                                         child='logging')
        )
        self._tasks_CFG.append(predic_log_task)

    def exportToCloud(self) -> None:
        [task.start() for task in self._tasks_CFG]
        return None


class BenchmarkPipeline(eeRFPipeline):
    def __init__(self, sar: List[ee.Image], optical: List[ee.Image],
                 dem: ee.Image, training_data: ee.FeatureCollection) -> None:
        super().__init__(sar, optical, dem, training_data)
        self._type = 'benchmark'

    def logging(self):
        logger = logging.eeLogger
        super().logging()

        # Sentinel - 2 Logging
        s2_log = logger.Sentinel2_logger(self._optical)
        s2_log_task = ee.batch.Export.table.toCloudStorage(
            collection=s2_log,
            bucket=self.bucket,
            description=f'{self._type}-Sentinel-2-log',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-Sentinel-2-log',
                                                         child='logging')
        )
        self._tasks_CFG.append(s2_log_task)


class DataCubePipeline(eeRFPipeline):
    def __init__(self, sar: List[ee.Image], optical: List[ee.Image],
                 dem: ee.Image, training_data: ee.FeatureCollection) -> None:
        super().__init__(sar, optical, dem, training_data)
        self._type = 'datacube'

    def logging(self, datacube_collection: ee.ImageCollection):
        super().logging()

        dc_logger = logging.DatacubeLogger(
            args=datacube_collection
        )

        tiles = dc_logger.tile_IDs()

        tile_task = ee.batch.Export.table.toCloudStorage(
            collection=tiles,
            description='data-cube-tile-ids-task',
            bucket=self.bucket,
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-tiles-log',
                                                         child='logging'),
            fileFormat='CSV'
        )
        self._tasks_CFG.append(tile_task)

        dates = dc_logger.datacube_dates()

        dc_date_task = ee.batch.Export.table.toCloudStorage(
            collection=dates,
            description='data-cube-dates-task',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-data-cube-dates-log',
                                                         child='logging'),
            bucket=self.bucket,
            fileFormat='CSV'
        )


class DataCubePipelineLSC(DataCubePipeline):

    def __init__(self, sar: ee.ImageCollection, optical: ee.ImageCollection,
                 dem: ee.Image, training_data: ee.FeatureCollection) -> None:
        sar_inputs = factories.s1_swath_images(
            collection=sar
        )

        optical_inputs = factories.datacube_img_factory(
            datacube_collection=optical,
            viewport=None
        )
        super().__init__(sar=sar_inputs, optical=optical_inputs, dem=dem,
                         training_data=training_data)
        self._optical_collection = optical
        self._sar_collection = sar

    def logging(self):

        logger = logging.eeLogger

        # logging
        # Sentiel - 1 Logging
        s1_log = logger.S1LSCLogger(self._sar_collection)
        s1_log_task = ee.batch.Export.table.toCloudStorage(
            collection=s1_log,
            bucket=self.bucket,
            description=f'{self._type}-Sentinel-1-log',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-Sentinel-1-log',
                                                         child='logging')
        )
        self._tasks_CFG.append(s1_log_task)

        # Training Data logging
        training_data = self._training_data

        training_task = ee.batch.Export.table.toCloudStorage(
            collection=training_data,
            bucket=self.bucket,
            description=f'{self._type}-training-data',
            fileFormat='SHP',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-training-data',
                                                         child='training-data')
        )
        self._tasks_CFG.append(training_task)

        lookup = logger.lookup(
            collection=self.samples,
            label_col=self.land_cover,
            value_col='land_value',
            colors=colors.Colors.to_eeDict()
        )
        look_log_task = ee.batch.Export.table.toCloudStorage(
            collection=lookup,
            bucket=self.bucket,
            description=f'{self._type}-lookup',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-training-data-lookup',
                                                         child='training-data')
        )
        self._tasks_CFG.append(look_log_task)

        log_predictors = logger.predictors(self.predictors)
        predic_log_task = ee.batch.Export.table.toCloudStorage(
            collection=log_predictors,
            bucket=self.bucket,
            description=f'{self._type}-predictors',
            fileFormat='CSV',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-predictors',
                                                         child='logging')
        )
        self._tasks_CFG.append(predic_log_task)

        # DataCube Logging
        dc_logger = logging.DatacubeLogger(
            args=self._optical_collection
        )

        tiles = dc_logger.tile_IDs()

        tile_task = ee.batch.Export.table.toCloudStorage(
            collection=tiles,
            description='data-cube-tile-ids-task',
            bucket=self.bucket,
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-tiles-log',
                                                         child='logging'),
            fileFormat='CSV'
        )
        self._tasks_CFG.append(tile_task)

        dates = dc_logger.datacube_dates()

        dc_date_task = ee.batch.Export.table.toCloudStorage(
            collection=dates,
            description='data-cube-dates-task',
            fileNamePrefix=self._child_cloud_path.format(root=self.root, phase=self.caseNumber,
                                                         type=self._type,
                                                         filename=f'{self._type}-data-cube-dates-log',
                                                         child='logging'),
            bucket=self.bucket,
            fileFormat='CSV'
        )
        self._tasks_CFG.append(dc_date_task)

        return None

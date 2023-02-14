from typing import Any, Dict, List

import ee


class CloudTasks(ee.batch.Export):
    def __init__(self):
        super().__init__()

    @classmethod
    def image_task(cls, image: ee.Image, description: str = None, bucket: str = None,
                   fileNamePrefix: str = None, region: ee.Geometry = None,
                   scale: int = None, crs: str = None, maxPixels: int = 1e13,
                   shardSize: int = 256, fileDimensions: List[int] = None,
                   fileFormat: str = None, formatOptions: Dict[str, Any] = None) -> ee.batch.Task:
        crs = 'EPSG:4326' if crs is None else crs
        fileFormat = 'GeoTIFF' if fileFormat is None else fileFormat
        formatOptions = {
            'cloudOptimized': True} if formatOptions is None else formatOptions

        if fileDimensions is not None:
            valid_dimensions = any(
                [i % shardSize == 0 for i in fileDimensions])
            if not valid_dimensions:
                raise ee.EEException(
                    f"File Dimensions are Not Valid: {shardSize}: {fileDimensions}")

        task_config = {
            'image': image,
            'description': description,
            'bucket': bucket,
            'fileNamePrefix': fileNamePrefix,
            'region': region,
            'maxPixels': maxPixels,
            'scale': scale,
            'fileFormat': fileFormat,
            'formatOptions': formatOptions
        }
        return cls.image.toCloudStorage(**task_config)

    @classmethod
    def table_task(cls, collection: ee.FeatureCollection, description: str = None,
                   bucket: str = None, fileNamePrefix: str = None, fileFormat: str = None,
                   selectors: List[str] = None):
        fileFormat = 'CSV' if fileFormat is None else fileFormat
        task_config = {
            'collection': collection,
            'description': description,
            'bucket': bucket,
            'fileNamePrefix': fileNamePrefix,
            'fileFormat': fileFormat,
            'selectors': selectors
        }
        return cls.table.toCloudStorage(**task_config)

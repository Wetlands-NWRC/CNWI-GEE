import os

from abc import ABC
from dataclasses import dataclass, field
from typing import Union

import ee

@dataclass
class CloudTasks(ABC):
    eeobj: Union[ee.FeatureCollection, ee.Image]
    description: str = field(default=None)
    bucket: str = field(default=os.environ.get('BUCKET', None))
    filename_prefix: str = field(default=None)
    file_format: str = field(default=None)
    
    def __post_init__(self):
        self.task: ee.batch.Task = None


@dataclass
class CloudTableTask(CloudTasks):
    eeobj: ee.FeatureCollection
    description: str = field(default='My-Table-Cloud-Task')
    file_format: str = field(default="CSV")

    def __post_init__(self):
        self.task = ee.batch.Export.table.toCloudStorage(
            collection=self.eeobj,
            description=self.description,
            bucket=self.bucket,
            fileFormat=self.file_format,
            fileNamePrefix=self.filename_prefix
        )


@dataclass
class CloudImageTask(CloudTasks):
    eeobj: ee.Image
    region: ee.Geometry = field(default=None)
    scale: int = 10
    crs: str = field(default='EPSG:4326')
    max_pixels: int = 1e13
    shard_size: int = 1000
    file_dim: list[int] = field(default_factory=lambda :[1000, 1000])
    file_format: str = field(default="GeoTIFF")
    
    def __post_init__(self):
        self.task = ee.batch.Export.image.toCloudStorage(
            image=self.eeobj,
            description=self.description,
            bucket=self.bucket,
            fileNamePrefix=self.filename_prefix,
            region=self.region,
            scale=self.scale,
            crs=self.crs,
            maxPixels=self.max_pixels,
            shardSize=self.shard_size,
            fileDimensions=self.file_dim,
            fileFormat=self.file_format
        )
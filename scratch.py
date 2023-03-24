from abc import ABC, abstractmethod
from typing import Any

import ee

ee.Initialize()

class ImageFactory(ABC):
    args: Any

    def get_image(self) -> ee.Image():
        pass


class Sentinel1V(ImageFactory):
    def get_image(self) -> ee.Image():
        """constructs a DV or SV image based of the args"""
        return ee.Image(self.args).select('V.*')


class Sentinel2(ImageFactory):
    def get_image(self) -> ee.Image():
        return self.select('B.*')


class Dem(ImageFactory):
    def get_image(self) -> ee.Image:
        return ee.Image(self.args).select('elevation')


class DataCubeImage(ImageFactory):        
    def get_image(self) -> ee.Image():
        pass        


class ImageCollectionFactory(ee.ImageCollection):
    _ARGS: str = None
    def __init__(self, dates: tuple[str], aoi: ee.Geometry):
        self.dates = dates
        self.aoi = aoi
        super().__init__(self._ARGS)


class S1DVCollection(ImageCollectionFactory):
    _ARGS = "COPERNICUS/S1_GRD"
    
    def get_collection(self) -> ee.ImageCollection:
        return self.filterBounds(self.aoi).filterDate(*self.dates)
obj = S1DVCollection(None, None)
t = ' '

class DataCubeCollection(ImageCollectionFactory):
    def get_collection():
        pass

DataCubeImage()
from abc import ABC
from typing import Union
import ee


class ImageFactory(ABC):
    args: Union[ee.Image, ee.ImageCollection]
    
    def get_image(self) -> ee.Image:
        pass


class Sentinel1V(ImageFactory):
    def get_image(self) -> ee.Image:
        return ee.Image(self.args).select('V.*')


class Sentinel2(ImageFactory):
    def get_image(self) -> ee.Image:
        return ee.Image(self.args).select('B.*')


class DEM(ImageFactory):
    def get_image(self) -> ee.Image:
        return ee.Image(self.args).select('elevation')


class DataCube(ImageFactory):
    def get_image(self) -> ee.Image:
        return super().get_image()


class ALOS(ImageFactory):
    def get_image(self, aoi: ee.Geometry, target_yyyy: int = 2018) -> ee.Image:
        instance: ee.ImageCollection = self.args.filterDate(target_yyyy, (target_yyyy + 1))\
            .filterBounds(aoi)
        return instance.mosaic().select('H.*')

from abc import ABC
from typing import Any
import ee


class ImageFactory(ABC):
    args: Any
    
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
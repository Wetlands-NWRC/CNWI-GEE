from abc import ABC
from typing import Union
import ee


class ImageFactory(ABC):
    def __init__(self, args: Union[str, ee.ImageCollection]) -> None:
        self.args = args
        super().__init__()
    
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
    def get_image(self, target_yyyy: int = 2018) -> ee.Image:
        date = f'{target_yyyy}', f'{target_yyyy + 1}'
        return self.args.filterDate(*date).first().select('H.*')
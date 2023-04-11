from abc import ABC, abstractmethod
from typing import Any

import ee

ee.Initialize()


class Sentinel1V(ImageFactory):
    def get_image(self) -> ee.Image():
        """constructs a DV or SV image based of the args"""
        return ee.Image(self.args).select('V.*')


class Sentinel2(ImageFactory):
    def get_image(self, qa_bands: bool = False) -> ee.Image():
        img = ee.Image(self.args)
        return img if not qa_bands else img.select("B.*")


class Dem(ImageFactory):
    def get_image(self) -> ee.Image:
        return ee.Image(self.args).select('elevation')


class DataCubeImage(ImageFactory):
    def _parse_dc_collection(self):
        """"""
        pass
      
    def get_image(self) -> List[ee.Image()]:
        pass        

class Phase(ImageFactory):
    """USed to create a phase images.

    Args:
        ImageFactory (): _description_
    """
    def get_image(self) -> ee.Image():
        return super().get_image()


class Alos(ImageFactory):
    def get_image(self, year: int, aoi: ee.Geometry):
        """_summary_

        Args:
            year (int): _description_
            aoi (ee.Geometry): _description_

        Returns:
            _type_: _description_
        """
        return self.arg

Alos().get_image()

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
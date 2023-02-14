from abc import ABC
import ee

import bands as dc_bands

class DataCubeCollection:
    def __new__(cls, asset_id: str, viewport: ee.Geometry = None) -> ee.ImageCollection:
        instance = ee.ImageCollection(asset_id)
        
        if viewport is not None:
            instance = instance.filterBounds(viewport)
        
        src = [ _.name for _ in dc_bands.DataCubeBands]
        dest = [_.value for _ in dc_bands.DataCubeBands]
        return instance.select(src, dest)


class _Stack(ABC):
    pass


class DataCubeStack(_Stack):
    def __new__(cls, datacubecollection, s1, dem) -> ee.Image:
        # apply filtering
        # create derivaitves
        pass


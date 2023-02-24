from typing import Iterable, Union

import ee

from . import struct

class S1Collection64:
    
    def __new__(cls, viewport: ee.Geometry = None) -> ee.ImageCollection:
        asset_ids = [
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015452_20180609T015517_011290_014BA0_39FD",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015517_20180609T015542_011290_014BA0_2658",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015542_20180609T015616_011290_014BA0_EE30",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015454_20180715T015519_011815_015BE0_0362",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015519_20180715T015544_011815_015BE0_D8D7",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015544_20180715T015618_011815_015BE0_8287",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015503_20180913T015528_012690_0176B4_78B3",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015528_20180913T015553_012690_0176B4_0EB4",
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015553_20180913T015613_012690_0176B4_EB44"
        ]
        
        imgs = [ee.Image(_) for _ in asset_ids]
        
        instance = ee.ImageCollection(imgs)
        
        if viewport is not None:
            instance = instance.filterBounds(viewport)

        return instance.map(lambda x: x.set('date', x.date().format('YYYY-MM-dd')))



class Williston_A_S2_IL(struct.ImageList):
    def __init__(self, images: Iterable[Union[str, ee.Image]]) -> None:
        images = []
        super().__init__(images)


class Williston_A_S1_IL(struct.ImageList):
    def __init__(self, images: Iterable[Union[str, ee.Image]]) -> None:
        super().__init__(images)
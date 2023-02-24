import os
import sys

from dataclasses import dataclass
from typing import Iterable, Union

import ee

from . import struct
from . import datacube

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from cnwi import inputs

class S1Collection64(struct.ImageList):
    
    def __init__(self):
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
        images = [ee.Image(_).set('date', ee.Image(_).date().format('YYYY-MM-dd')) 
                  for _ in asset_ids]
        super().__init__(images)


class Williston_A_S2_IL(struct.ImageList):
    def __init__(self) -> None:
        """Williston A Senteniel 2 TOA GEE native assets. Only Valid for AOI A
        """        
        images = [
            'COPERNICUS/S2/20180519T191909_20180519T192621_T10UEF',
            'COPERNICUS/S2/20180728T191909_20180728T192508_T10UEF'
        ]
        super().__init__(images)


class Williston_A_S1_IL(struct.ImageList):
    def __init__(self) -> None:
        images = [
            'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180517T142651_20180517T142716_010962_014115_CA58',
            'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180728T142655_20180728T142720_012012_0161D6_96BF'
        ]
        super().__init__(images)


class WillistonDataCube(datacube.DataCube):
    def __new__(cls) -> ee.ImageCollection:
        asset_id = ""
        return super().__new__(asset_id)
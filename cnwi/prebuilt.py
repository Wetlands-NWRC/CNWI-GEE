from typing import List
from dataclasses import dataclass, field

import ee


@dataclass(frozen=True)
class PreBuildDataSet:
    s1: list[str]
    s2: list[str]


@dataclass(frozen=True)
class WillistonA(PreBuildDataSet):
    s1: list = field(default_factory=lambda: [
        'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180517T142651_20180517T142716_010962_014115_CA58',
        'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180728T142655_20180728T142720_012012_0161D6_96BF'
    ])
    s2: list = field(default_factory=lambda: [
        'COPERNICUS/S2_HARMONIZED/20180519T191909_20180519T192621_T10UEF',
        'COPERNICUS/S2_HARMONIZED/20180728T191909_20180728T192508_T10UEF'
    ])
    region: str = "users/ryangilberthamilton/BC/williston/williston_sub_a_2019"


@dataclass(frozen=True)
class WillistonDataCube:
    asset_id: str = field(default="projects/fpca-336015/assets/williston-cba")
    s1: List[List[str]] = field(default_factory= lambda: [
       "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015452_20180609T015517_011290_014BA0_39FD",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015517_20180609T015542_011290_014BA0_2658",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015542_20180609T015616_011290_014BA0_EE30",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015454_20180715T015519_011815_015BE0_0362",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015519_20180715T015544_011815_015BE0_D8D7",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015544_20180715T015618_011815_015BE0_8287",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015503_20180913T015528_012690_0176B4_78B3",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015528_20180913T015553_012690_0176B4_0EB4",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015553_20180913T015613_012690_0176B4_EB44",
    ])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Pre - built Image Collections
#TODO add asset strings to each class
class _PreBuiltImageCollection(ee.ImageCollection):
    ARGS: str 
    
    def __init__(self):
        super().__init__(self.ARGS)


class ALOS(_PreBuiltImageCollection):
    ARGS = "JAXA/ALOS/PALSAR-2/Level2_2/ScanSAR"


class Sentinel1(_PreBuiltImageCollection):
    ARGS = "COPERNICUS/S1_GRD"


class Sentinel2SR(_PreBuiltImageCollection):
    ARGS = "COPERNICUS/S2_SR"


class Sentinel2TOA(_PreBuiltImageCollection):
    ARGS = "COPERNICUS/S2_HARMONIZED"


class AAFC(_PreBuiltImageCollection):
    ARGS = "AAFC/ACI"


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Pre Built Images
class _PreBuiltImage(ee.Image):
    ARGS: str
    
    def __init__(self):
        super().__init__(self.ARGS, None)


class NASA_DEM(_PreBuiltImage):
    ARGS = "NASA/NASADEM_HGT/001"


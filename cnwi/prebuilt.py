from dataclasses import dataclass, field

import ee

from . import imgs

@dataclass(frozen=True)
class PreBuildDataSet:
    s1: list[str]
    s2: list[str]
    dem: imgs.NASADEM_HGT = imgs.NASADEM_HGT()
    
    @property
    def sentinel1(self):
        return [imgs.Sentinel1(_) for _ in self.s1]
    
    @property
    def sentinel2(self):
        return [imgs.Sentinel2(_) for _ in self.s2]
    

@dataclass(frozen=True)
class WillistonA(PreBuildDataSet):
    s1: list = field(default_factory=lambda: [
        'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180517T142651_20180517T142716_010962_014115_CA58',
        'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180728T142655_20180728T142720_012012_0161D6_96BF'
    ])
    s2: list = field(default_factory=lambda: [
        'COPERNICUS/S2/20180519T191909_20180519T192621_T10UEF',
        'COPERNICUS/S2/20180728T191909_20180728T192508_T10UEF'
    ])


@dataclass(frozen=True)
class WillistonDataCube:
    asset_id: str = field("projects/fpca-336015/assets/williston-cba")
    s1: list = field(default_factory= lambda: [
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015452_20180609T015517_011290_014BA0_39FD",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015517_20180609T015542_011290_014BA0_2658",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015542_20180609T015616_011290_014BA0_EE30",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015454_20180715T015519_011815_015BE0_0362",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015519_20180715T015544_011815_015BE0_D8D7",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015544_20180715T015618_011815_015BE0_8287",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015503_20180913T015528_012690_0176B4_78B3",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015528_20180913T015553_012690_0176B4_0EB4",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015553_20180913T015613_012690_0176B4_EB44"
    ])

    @property
    def sentinel1(self) -> list[ee.Image]:
        # TODO overdied with image collection parsers
        pass
    
    @property
    def sentinel2(self) -> list[ee.Image]:
        # TODO override with data cube parser
        pass
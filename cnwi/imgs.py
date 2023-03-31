from abc import ABC
from typing import Union, Dict
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


class eeDataCube(ee.Image):
    BANDS = {
        0: 'a_spri_b01_60m',
        1: 'a_spri_b02_10m',
        2: 'a_spri_b03_10m',
        3: 'a_spri_b04_10m',
        4: 'a_spri_b05_20m',
        5: 'a_spri_b06_20m',
        6: 'a_spri_b07_20m',
        7: 'a_spri_b08_10m',
        8: 'a_spri_b08a_20m',
        9: 'a_spri_b11_20m',
        10: 'a_spri_b12_20m',
        11: 'a_spri_doy_y1',
        12: 'a_spri_doy_y2',
        13: 'a_spri_imgyear_y1',
        14: 'a_spri_imgyear_y2',
        15: 'a_spri_weight_y2',
        16: 'a_spri_weight_y2_base',
        17: 'a_spri_weight_y2_swiradj',
        18: 'b_summ_b01_60m',
        19: 'b_summ_b02_10m',
        20: 'b_summ_b03_10m',
        21: 'b_summ_b04_10m',
        22: 'b_summ_b05_20m',
        23: 'b_summ_b06_20m',
        24: 'b_summ_b07_20m',
        25: 'b_summ_b08_10m',
        26: 'b_summ_b08a_20m',
        27: 'b_summ_b11_20m',
        28: 'b_summ_b12_20m',
        29: 'b_summ_doy_y1',
        30: 'b_summ_doy_y2',
        31: 'b_summ_imgyear_y1',
        32: 'b_summ_imgyear_y2',
        33: 'b_summ_weight_y2',
        34: 'b_summ_weight_y2_base',
        35: 'b_summ_weight_y2_swiradj',
        36: 'c_fall_b01_60m',
        37: 'c_fall_b02_10m',
        38: 'c_fall_b03_10m',
        39: 'c_fall_b04_10m',
        40: 'c_fall_b05_20m',
        41: 'c_fall_b06_20m',
        42: 'c_fall_b07_20m',
        43: 'c_fall_b08_10m',
        44: 'c_fall_b08a_20m',
        45: 'c_fall_b11_20m',
        46: 'c_fall_b12_20m',
        47: 'c_fall_doy_y1',
        48: 'c_fall_doy_y2',
        49: 'c_fall_imgyear_y1',
        50: 'c_fall_imgyear_y2',
        51: 'c_fall_weight_y2',
        52: 'c_fall_weight_y2_base',
        53: 'c_fall_weight_y2_swiradj',
    }
    
    BAND_PREFIX = {
        'spring': 'a_spri_b',
        'summer': 'b_summ_b',
        'fall': 'c_fall_b'
    }
    
    @classmethod
    def show_bands(cls) -> dict:
        return cls.BANDS
    
    @classmethod
    def show_band_prefix(cls):
        return cls.BAND_PREFIX
    
    def _parse_dc_tiles(self, obj: ee.ImageCollection) -> ee.Image:
        band_idx = list(self.BANDS.keys())
        band_names = list(self.BANDS.values())
        return obj.select(band_idx, band_names).mosaic()

    def __init__(self, dc_collection: ee.ImageCollection):
        """Extracts the seasonal composites from data cube images"""        
        super().__init__(self._parse_dc_tiles(dc_collection), None)
    
    def get_seasonal_composites(self) -> Dict[str, ee.Image]:
        """Returns a Dictonary where the keys are the season type i.e. spring, summer, fall, and the
        key is the resulting composite"""
        seasons = 'spring', 'summer', 'fall'
        return {k: self.select(self.BAND_PREFIX.get(k)+ '.*') for k in seasons}


class _S2(ee.Image):
    BANDS = {}

    @classmethod
    def show_bands(cls) -> dict:
        return cls.BANDS
    
    def __init__(self, args: str, include_qa: bool = False):
        """Constructs a Sentinel 2 SR image from a string assumed to be a sentinel 2 sr asset id.
        by default does not include the QA bands, only spectral bands"""
        img = ee.Image(args).select(list(self.BANDS.keys())) if include_qa == False else ee.Image(args)
        super().__init__(img, None)


class S2SR(_S2):
    BANDS = {
        0 : 'B1',
        1 : 'B2',
        2 : 'B3',
        3 : 'B4',
        4 : 'B5',
        5 : 'B6',
        6 : 'B7',
        7 : 'B8',
        8 : 'B8A',
        9:  'B11',
        10:  'B12',
    }

class S2TOA(_S2):
    BANDS = {
        0: "B1",
        1: "B2",
        2: "B3",
        3: "B4",
        4: "B5",
        5: "B6",
        6: "B7",
        7: "B8",
        8: "B8A",
        9: "B9",
        10:"B10",
        11:"B11",
        12:"B12",
    }

class _S1(ee.Image):
    BANDS = {}
    
    @classmethod
    def show_bands(cls):
        return cls.BANDS
    
    def __init__(self, args=None):
        """Represents an Earth Engine Native Asset"""
        super().__init__(ee.Image(args).select(*self.BANDS.keys()), None)


class S1DV(_S1):
    BANDS = {
        0: 'VV',
        1: 'VH',
    }


class S1DH(_S1):
    BANDS = {
        0: 'HH',
        1: 'HV',
    }


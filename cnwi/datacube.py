from dataclasses import dataclass, field
from typing import Dict

import ee

from . import derivatives as d

@dataclass(frozen=True)
class DataCubeBands:
    bands: Dict[int, str] = field(default_factory= lambda: {
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
    })
    
    band_prefix: Dict[str, str] = field(default_factory= lambda: {
        'spring': 'a_spri_b',
        'summer': 'b_summ_b',
        'fall': 'c_fall_b'
    })



def prep_data_cube(col: ee.ImageCollection):
    """ Handles building data cube collection that can be used downstream """
    # Standardize band names to S2 
    s2_names = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
    
    # input
    first = col.first()
    
    ## Spring Bands
    spring_prefix = 'a_spri_b.*'
    spring_bands: ee.List = first.select(spring_prefix).bandNames()
    
    ## Summer Bands
    summer_prefix = 'b_summ_b.*'
    summer_bands: ee.List = first.select(summer_prefix).bandNames()
    
    ## Fall Bands
    fall_prefix = 'c_fall_b.*'
    fall_bands: ee.List = first.select(fall_prefix).bandNames()

    # cat bands, selection 
    concat = spring_bands.cat(summer_bands).cat(fall_bands)
    
    ## Remapping Band Names to s2 standard
    spring_new = s2_names
    summer_new = [f'{_}_1' for _ in s2_names]
    fall_new = [f'{_}_2' for _ in s2_names]
    
    new_band_names = spring_new + summer_new + fall_new
    
    return col.map(lambda x: x.select(concat, new_band_names))


def build_data_cube_inpts(col: ee.ImageCollection)-> ee.Image:
    # create the objects to be mapped
    
    ##NDVI
    spring_NDVI = d.NDVI()
    summer_NDVI = d.NDVI(nir='B8_1', red='B4_1')
    fall_NDVI = d.NDVI(nir='B8_2', red='B4_2')
    
    ##SAVI
    spring_SAVI = d.SAVI()
    summer_SAVI = d.SAVI(nir='B8_1', red='B4_1')
    fall_SAVI = d.SAVI(nir='B8_2', red='B4_2')

    ##Tassel Cap
    spring_tc = d.TasselCap()
    summer_tc = d.TasselCap(
        blue="B2_1",
        red='B4_1',
        green='B3_1',
        nir='B8_1',
        swir_1='B11_1',
        swir_2='B12_1'
    )

    fall_tc = d.TasselCap(
        blue="B2_2",
        red='B4_2',
        green='B3_2',
        nir='B8_2',
        swir_1='B11_2',
        swir_2='B12_2'
    )
    
    return col.map(spring_NDVI).map(summer_NDVI).map(fall_NDVI).map(spring_SAVI).map(summer_SAVI).\
        map(fall_SAVI).map(spring_tc).map(summer_tc).map(fall_tc).mosaic()
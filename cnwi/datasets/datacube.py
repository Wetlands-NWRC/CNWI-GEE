from __future__ import annotations

import os
import sys

from abc import ABC
from datetime import datetime
from enum import Enum

import ee

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from eelib import bands

class DataCubeBands(Enum):
    """Original Data Cube Band Mappings"""
    B0 = 'a_spri_b01_60m'
    B1 = 'a_spri_b02_10m'
    B2 = 'a_spri_b03_10m'
    B3 = 'a_spri_b04_10m'
    B4 = 'a_spri_b05_20m'
    B5 = 'a_spri_b06_20m'
    B6 = 'a_spri_b07_20m'
    B7 = 'a_spri_b08_10m'
    B8 = 'a_spri_b08a_20m'
    B9 = 'a_spri_b11_20m'
    B10 = 'a_spri_b12_20m'
    B11 = 'a_spri_doy_y1'
    B12 = 'a_spri_doy_y2'
    B13 = 'a_spri_imgyear_y1'
    B14 = 'a_spri_imgyear_y2'
    B15 = 'a_spri_weight_y2'
    B16 = 'a_spri_weight_y2_base'
    B17 = 'a_spri_weight_y2_swiradj'
    B18 = 'b_summ_b01_60m'
    B19 = 'b_summ_b02_10m'
    B20 = 'b_summ_b03_10m'
    B21 = 'b_summ_b04_10m'
    B22 = 'b_summ_b05_20m'
    B23 = 'b_summ_b06_20m'
    B24 = 'b_summ_b07_20m'
    B25 = 'b_summ_b08_10m'
    B26 = 'b_summ_b08a_20m'
    B27 = 'b_summ_b11_20m'
    B28 = 'b_summ_b12_20m'
    B29 = 'b_summ_doy_y1'
    B30 = 'b_summ_doy_y2'
    B31 = 'b_summ_imgyear_y1'
    B32 = 'b_summ_imgyear_y2'
    B33 = 'b_summ_weight_y2'
    B34 = 'b_summ_weight_y2_base'
    B35 = 'b_summ_weight_y2_swiradj'
    B36 = 'c_fall_b01_60m'
    B37 = 'c_fall_b02_10m'
    B38 = 'c_fall_b03_10m'
    B39 = 'c_fall_b04_10m'
    B40 = 'c_fall_b05_20m'
    B41 = 'c_fall_b06_20m'
    B42 = 'c_fall_b07_20m'
    B43 = 'c_fall_b08_10m'
    B44 = 'c_fall_b08a_20m'
    B45 = 'c_fall_b11_20m'
    B46 = 'c_fall_b12_20m'
    B47 = 'c_fall_doy_y1'
    B48 = 'c_fall_doy_y2'
    B49 = 'c_fall_imgyear_y1'
    B50 = 'c_fall_imgyear_y2'
    B51 = 'c_fall_weight_y2'
    B52 = 'c_fall_weight_y2_base'
    B53 = 'c_fall_weight_y2_swiradj'


class GC_ImageCollection:
    
    def __new__(cls, asset_id) -> ee.ImageCollection:
        return ee.ImageCollection(asset_id)


class DataCube(GC_ImageCollection):
    def __new__(cls, asset_id) -> list[ee.Image]:
        instance = ee.ImageCollection(asset_id).select(
            selectors=[str(_.name) for _ in DataCubeBands],
            opt_names=[str(_.value) for _ in DataCubeBands]
        )
        return instance
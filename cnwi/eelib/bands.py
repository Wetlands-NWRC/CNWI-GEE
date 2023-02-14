from enum import Enum


class S2TOA(Enum):
    B1 = 'Aerosols'
    B2 = 'Blue'
    B3 = 'Green'
    B4 = 'Red'
    B5 = 'Red Edge 1'
    B6 = 'Red Edge 2'
    B7 = 'Red Edge 3'
    B8 = 'NIR'
    B8A = 'Red Edge 4'
    B9 = 'Water vapor'
    B10 = 'Cirrus'
    B11 = 'SWIR 1'
    B12 = 'SWIR 2'


class S2SR(Enum):
    B1 = 'Aerosols'
    B2 = 'Blue'
    B3 = 'Green'
    B4 = 'Red'
    B5 = 'Red Edge 1'
    B6 = 'Red Edge 2'
    B7 = 'Red Edge 3'
    B8 = 'NIR'
    B8A = 'Red Edge 4'
    B11 = 'SWIR 1'
    B12 = 'SWIR 2'


class S2DCParsed(Enum):
    """After a band offset has been added and Composite has been parsed into
    seperate Seasonal Composites"""
    B1 = 'Aerosols'
    B2 = 'Blue'
    B3 = 'Green'
    B4 = 'Red'
    B5 = 'Red Edge 1'
    B6 = 'Red Edge 2'
    B7 = 'Red Edge 3'
    B8 = 'NIR'
    B9 = 'Red Edge 4'
    B10 = 'SWIR 1'
    B11 = 'SWIR 2'


class WillistonCBA(Enum):
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

    @classmethod
    def get_seasons(cls) -> dict:
        spring_prefix = None
        summer_prefix = None
        fall_prefix = None

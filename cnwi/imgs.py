from abc import ABC
from typing import Union, Dict
import ee


class ALOS(ee.Image):
    def __init__(self, target_yyyy: int = 2018):
        instance = ee.ImageCollection("JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH")\
            .filterDate(f'{target_yyyy}', f'{target_yyyy + 1}').select('H.*')
        super().__init__(instance.first(), None)


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
    

    def __init__(self, dc_collection: ee.ImageCollection):
        """Extracts the seasonal composites from data cube images"""        
        super().__init__(self._parse_dc_tiles(dc_collection), None)
    
    def _parse_dc_tiles(self, obj: ee.ImageCollection) -> ee.Image:
        band_idx = list(self.BANDS.keys())
        band_names = list(self.BANDS.values())
        return obj.select(band_idx, band_names).mosaic()
    
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


class NASA_DEM(ee.Image):
    def __init__(self) -> None:
        super().__init__(ee.Image("NASA/NASADEM_HGT/001").select('elevation'))


class S2Cloudless(ee.Image):
    CLOUD_FILTER = 60
    CLD_PRB_THRESH = 40
    NIR_DRK_THRESH = 0.15
    CLD_PRJ_DIST = 2
    BUFFER = 100
    
    def __init__(self, aoi, start_date, end_date):
        """ Adapted from here: https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless"""
        s2_sr_cld_col = self.get_s2_sr_cld_col(aoi, start_date, end_date)
        s2_sr_median = (s2_sr_cld_col.map(self._add_cld_shdw_mask)
                             .map(self._apply_cld_shdw_mask)
                             .median())
        super().__init__(s2_sr_cld_col, None)
    
    def _get_s2_sr_cld_col(self, aoi, start_date, end_date):
        # Import and filter S2 SR.
        s2_sr_col = (ee.ImageCollection('COPERNICUS/S2_SR')
            .filterBounds(aoi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lte('CLOUDY_PIXEL_PERCENTAGE', self.CLOUD_FILTER)))

        # Import and filter s2cloudless.
        s2_cloudless_col = (ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
            .filterBounds(aoi)
            .filterDate(start_date, end_date))

        # Join the filtered s2cloudless collection to the SR collection by the 'system:index' property.
        return ee.ImageCollection(ee.Join.saveFirst('s2cloudless').apply(**{
            'primary': s2_sr_col,
            'secondary': s2_cloudless_col,
            'condition': ee.Filter.equals(**{
                'leftField': 'system:index',
                'rightField': 'system:index'
            })
        }))
    
    def _add_cloud_bands(self, img):
        # Get s2cloudless image, subset the probability band.
        cld_prb = ee.Image(img.get('s2cloudless')).select('probability')

        # Condition s2cloudless by the probability threshold value.
        is_cloud = cld_prb.gt(self.CLD_PRB_THRESH).rename('clouds')

        # Add the cloud probability layer and cloud mask as image bands.
        return img.addBands(ee.Image([cld_prb, is_cloud]))

    def _add_shadow_bands(self, img):
        # Identify water pixels from the SCL band.
        not_water = img.select('SCL').neq(6)

        # Identify dark NIR pixels that are not water (potential cloud shadow pixels).
        SR_BAND_SCALE = 1e4
        dark_pixels = img.select('B8').lt(self.NIR_DRK_THRESH*SR_BAND_SCALE).multiply(not_water).rename('dark_pixels')

        # Determine the direction to project cloud shadow from clouds (assumes UTM projection).
        shadow_azimuth = ee.Number(90).subtract(ee.Number(img.get('MEAN_SOLAR_AZIMUTH_ANGLE')));

        # Project shadows from clouds for the distance specified by the CLD_PRJ_DIST input.
        cld_proj = (img.select('clouds').directionalDistanceTransform(shadow_azimuth, self.CLD_PRJ_DIST*10)
            .reproject(**{'crs': img.select(0).projection(), 'scale': 100})
            .select('distance')
            .mask()
            .rename('cloud_transform'))

        # Identify the intersection of dark pixels with cloud shadow projection.
        shadows = cld_proj.multiply(dark_pixels).rename('shadows')

        # Add dark pixels, cloud projection, and identified shadows as image bands.
        return img.addBands(ee.Image([dark_pixels, cld_proj, shadows]))

    def _add_cld_shdw_mask(self, img):
        # Add cloud component bands.
        img_cloud = self._add_cloud_bands(img)

        # Add cloud shadow component bands.
        img_cloud_shadow = self._add_shadow_bands(img_cloud)

        # Combine cloud and shadow mask, set cloud and shadow as value 1, else 0.
        is_cld_shdw = img_cloud_shadow.select('clouds').add(img_cloud_shadow.select('shadows')).gt(0)

        # Remove small cloud-shadow patches and dilate remaining pixels by BUFFER input.
        # 20 m scale is for speed, and assumes clouds don't require 10 m precision.
        is_cld_shdw = (is_cld_shdw.focalMin(2).focalMax(self.BUFFER*2/20)
            .reproject(**{'crs': img.select([0]).projection(), 'scale': 20})
            .rename('cloudmask'))

        # Add the final cloud-shadow mask to the image.
        return img_cloud_shadow.addBands(is_cld_shdw)
    
    def apply_cld_shdw_mask(self, img):
        # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
        not_cld_shdw = img.select('cloudmask').Not()

        # Subset reflectance bands and update their masks, return the result.
        return img.select('B.*').updateMask(not_cld_shdw)

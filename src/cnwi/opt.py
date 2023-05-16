from typing import Dict, Union

import ee


class Sentinel2SR(ee.ImageCollection):
    ARGS = 'COPERNICUS/S2_SR'
    
    def __init__(self):
        super().__init__(self.ARGS)


class S2Cloudless(ee.Image):
    CLOUD_FILTER = 60
    CLD_PRB_THRESH = 40
    NIR_DRK_THRESH = 0.15
    CLD_PRJ_DIST = 2
    BUFFER = 100
    
    def __init__(self, aoi, start_date, end_date):
        """ Adapted from here: https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless"""
        s2_sr_cld_col = self._get_s2_sr_cld_col(aoi, start_date, end_date)
        self.s2_sr = (s2_sr_cld_col.map(self._add_cld_shdw_mask)
                             .map(self._apply_cld_shdw_mask))
        super().__init__(self.s2_sr.median(), None)
    
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
    
    def _apply_cld_shdw_mask(self, img):
        # Subset the cloudmask band and invert it so clouds/shadow are 0, else 1.
        not_cld_shdw = img.select('cloudmask').Not()

        # Subset reflectance bands and update their masks, return the result.
        return img.select('B.*').updateMask(not_cld_shdw)

    def get_image_collection(self):
        return self.s2_sr

class DataCubeComposite(ee.ImageCollection):
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
    PREFIX = {
        'spring': 'a_spri_b',
        'summer': 'b_summ_b',
        'fall': 'c_fall_b'
    }
    
    @classmethod
    def show_band_prefix(cls) -> Dict[int, str]:
        return cls.PREFIX

    @classmethod
    def show_band_names(cls) -> Dict[int, str]:
        return cls.BANDS
    
    def __init__(self, args):
        super().__init__(args)

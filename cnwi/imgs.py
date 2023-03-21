import ee
import tagee


class Sentinel1:
    def __new__(cls, asset_id: str) -> ee.Image:
        """
        DV = VV + VH
        DH = HH + HV
        SV = VV
        SH = HH
        """
        image = ee.Image(asset_id)
        if 'DV' in asset_id or 'SV' in asset_id:
            image = image.select('V.*')
        elif 'DH' in asset_id or 'SH' in asset_id:
            image = image.select('H.*')
        else:
            raise TypeError("Not at Valid Sentinel 1 Asset - id")
        
        return image


class ALOS:
    def __new__(cls, target_yyyy: int = 2018, aoi: ee.Geometry = None) -> ee.Image:
        alos_collection = ee.ImageCollection("").filterDate(f'{target_yyyy}', f'{target_yyyy + 1}')
        if aoi is not None:
            alos_collection = alos_collection.filterBounds(aoi)
        return alos_collection.mean()


class Sentinel2:
    def __new__(cls) -> ee.Image:
        pass


class DataCube:
    TARGET_YEAR = 2018
    def __new__(cls) -> ee.Image:
        """Represents a Cloud back asset, images are from Geomatics Data Cube"""
        # access the parsing and date 
        pass


class DEM:
    def __new__(cls, asset_id: str, rectangle: ee.Geometry) -> ee.Image:
        # construct
        ee_obj = ee.Image(asset_id).select('elevation')
        return tagee.terrainAnalysis(ee_obj, rectangle)
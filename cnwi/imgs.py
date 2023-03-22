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
    def __new__(cls, asset_id: str) -> ee.Image:
        """Constructs a new ee.Image, the QA bands are not returned

        Args:
            asset_id (str): asset id of a sentinel 2 image

        Returns:
            ee.Image: a constricted image with only spectral bands selects
        """
        return ee.Image(asset_id).select('B.*')


class DataCube:
    TARGET_YEAR = 2018
    def __new__(cls, asset_id: str) -> ee.Image:
        """Represents a Cloud back asset, images are from Geomatics Data Cube"""
        # access the parsing and date 
        pass


class AAFC:
    def __new__(cls, target_yyyy: int = 2018, aoi: ee.Geometry = None) -> ee.Image:
        instance = ee.ImageCollection("AAFC/ACI").filterDate(target_yyyy, (target_yyyy + 1))
        if aoi is None:
            return instance.filterBounds(aoi).first()
        else:
            return instance.first()


class DEM(ee.Image):
    def __init__(self, args=None, version=None):
        super().__init__(args, version)
    
    def terrain_analysis(self, rectangle) -> ee.Image:
        return tagee.terrainAnalysis(self, rectangle)        


class NASADEM_HGT(DEM):
    def __init__(self):
        super().__init__("NASA/NASADEM_HGT/001", None)
    
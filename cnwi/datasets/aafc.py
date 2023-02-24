import enum

import ee


class Codes(enum.IntEnum):
    pass


class AAFC:
    
    def __new__(cls, target_year: int = 2018, viewport: ee.Geometry = None) -> ee.Image:
        instance = ee.ImageCollection("AAFC/ACI").filterDate(target_year, (target_year + 1))
        if viewport is None:
            return instance.filterBounds(viewport).first()
        else:
            return instance.first()

    def __init__(self) -> None:
        pass
    
    def create_mask(*values) -> ee.Image:
        pass
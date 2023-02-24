import ee


class CDEM:
    def __new__(cls, viewport: ee.Geometry = None) -> ee.Image:
        instance = ee.ImageCollection("NRCan/CDEM")

        if viewport is not None:
            return instance.filterBounds(viewport).mean()
        else:
            return instance.mean()

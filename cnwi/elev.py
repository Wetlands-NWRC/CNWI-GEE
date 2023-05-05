import ee
import tagee


class NASA_DEM(ee.Image):
    
    ARGS = "NASA/NASADEM_HGT/001"
    def __init__(self):
        super().__init__(self.ARGS)


def build_elevation_inpts(dem: ee.Image, aoi: ee.Geometry, ta: bool = True):
    dem = dem.select('elevation')
    if not ta:
        slope = ee.Terrain.slope(dem)
        return dem.addBands(slope)
    
    # do terrain analysis raise warning to the end user
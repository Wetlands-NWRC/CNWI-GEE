import warnings

import ee
import tagee

from . import sfilters as s


class NASA_DEM(ee.Image):
    
    ARGS = "NASA/NASADEM_HGT/001"
    def __init__(self):
        super().__init__(self.ARGS)


def build_rectangle(geom: ee.Geometry):
    """Creates a rectangle from a Feature Collection of Geometry"""
    if isinstance(geom, ee.FeatureCollection):
        geom = geom.geometry()
    else:
        geom = geom

    coords = geom.bounds().coordinates()

    listCoords = ee.Array.cat(coords, 1)
    xCoords = listCoords.slice(1, 0, 1)
    yCoords = listCoords.slice(1, 1, 2)

    xMin = xCoords.reduce('min', [0]).get([0, 0])
    xMax = xCoords.reduce('max', [0]).get([0, 0])
    yMin = yCoords.reduce('min', [0]).get([0, 0])
    yMax = yCoords.reduce('max', [0]).get([0, 0])

    return ee.Geometry.Rectangle(xMin, yMin, xMax, yMax)


def build_elevation_inpts(dem: ee.Image, aoi: ee.Geometry, ta: bool = True):
    GUASSIAN_BANDS =  ['Elevation', 'Slope', 'GaussianCurvature']
    PERONA_MALIK_BANDS = ['HorizontalCurvature', 'VerticalCurvature', 'MeanCurvature']
    
    dem = dem.select('elevation')
    if not ta:
        slope = ee.Terrain.slope(dem)
        return dem.addBands(slope)
    else:
        warnings.warn("Terrain Analysis as been Set to True... Please Note this is very memroy intenseve")
        # do terrain analysis raise warning to the end user
        dem_guas = s.gaussian_filter(3)
        pm = s.perona_malik()
        
        rectnalge = build_rectangle(aoi)

        dem_guas = dem_guas(dem)
        ta_gauss = tagee.terrainAnalysis(dem_guas, rectnalge).select(GUASSIAN_BANDS)
        
        dem_pm = pm(dem)
        ta_pm = tagee.terrainAnalysis(dem_pm, rectnalge).select(PERONA_MALIK_BANDS)
        
        return ee.Image.cat(ta_gauss, ta_pm)
from __future__ import annotations

from typing import Dict, List, Callable, Union

import ee
import tagee

from . import sfilters, funcs, bands, imgs
from . import derivatives as driv


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def sentinel1V(asset):
    """
    Constructs an ee.Image that represents a Dual Pol VV + VH image
    """
    return ee.Image(asset).select("V.*")

def sentinel1H(asset):
    return ee.Image(asset).select("H.*")
    

def alos(target_yyyy: int = 2018, aoi: ee.Geometry = None) -> ee.Image:
    alos_collection = ee.ImageCollection("").filterDate(f'{target_yyyy}', f'{target_yyyy + 1}')
    if aoi is not None:
        alos_collection = alos_collection.filterBounds(aoi)
    return alos_collection.mean().select('H.*')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def sentinel2(asset) -> ee.Image:
    return ee.Image(asset).select('B.*')


def data_cube(asset: str, aoi: ee.Geometry):
    dc = ee.ImageCollection(asset).filterBounds(aoi)
    # parse the data cube images into 3 seperate images, spring, summer, fall
    return funcs.data_cube_images

    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def aafc(target_yyyy: int = 2018, aoi: ee.Geometry = None) -> ee.Image:
    instance = ee.ImageCollection("AAFC/ACI").filterDate(target_yyyy, (target_yyyy + 1))
    if aoi is None:
        return instance.filterBounds(aoi).first()
    else:
        return instance.first()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def nasa_dem() -> ee.Image:
    return ee.Image("NASA/NASADEM_HGT/001").select('elevation')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def s2_inputs(assets: list[imgs.Sentinel2]) -> List[ee.Image]:
    # optcial inputs 
    s2s = [_.get_image() for _ in assets]
    ndvis = driv.batch_create_ndvi(s2s)
    savis = driv.batch_create_savi(s2s)
    tassels = driv.batch_create_tassel_cap(s2s)

    return [*s2s, *ndvis, *savis, *tassels]


def s1_inputs(assets: list[imgs.Sentinel1V], s_filter = None) ->List[ee.Image]:
    # prep the inputs
    s1s = [_.get_image() for _ in assets]
    # sar inputs
    s_filter = sfilters.boxcar(1) if s_filter is None else s_filter
    sar_pp1 = [s_filter(_) for _ in s1s]
    # sar derivatives
    ratios = driv.batch_create_ratio(
        images=sar_pp1,
        numerator='VV',
        denominator='VH'
    )
    return [*sar_pp1, *ratios]


def elevation_inputs(rectangle: ee.Geometry = None, image: ee.Image = None, s_filter: Dict[Callable, List[Union[str, int]]] = None):
    image = nasa_dem() if image is None else image
    def terrain_analysis(s_filter):
        if s_filter is None:
            s_filter = {
                sfilters.gaussian_filter(3): ['Elevation', 'Slope', 'GaussianCurvature'],
                sfilters.perona_malik(): ['HorizontalCurvature', 'VerticalCurvature', 'MeanCurvature']
            }
        
        out = []
        for filter, selector in s_filter.items():
            smoothed = filter(image)
            ta = tagee.terrainAnalysis(smoothed, rectangle).select(selector)
            out.append(ta)
            ta, smoothed = None, None
        return out
    
    if rectangle is None:
        s_filter = sfilters.gaussian_filter(3)
        smoothed = s_filter(image)
        slope = ee.Terrain.slope(smoothed)
        return [smoothed, slope]
    else:
        return terrain_analysis(s_filter=s_filter)
            

def data_cube_inputs(collection: ee.ImageCollection) -> List[ee.Image]:
    band_prefix = {"spring": "a_spri_b.*", "summer": 'b_summ_b.*', "fall": "c_fall_b.*"}
    
    old, new = bands.DataCube.bands()
    col = collection.select(old, new)
    
    s2_sr = bands.S2SR.bands()[0]
    band_idx = [idx for idx, _ in enumerate(s2_sr)]
    spring_col = col.select(band_prefix.get("spring")).select(band_idx, s2_sr)
    summer_col =  col.select(band_prefix.get('summer')).select(band_idx, s2_sr)
    fall_col = col.select(band_prefix.get('fall')).select(band_idx, s2_sr)    

    s2s = [spring_col.mosaic(), summer_col.mosaic(), fall_col.mosaic()]

    ndvis = driv.batch_create_ndvi(s2s)
    savis = driv.batch_create_savi(s2s)
    tassels = driv.batch_create_tassel_cap(s2s)

    return [*s2s, *ndvis, *savis, *tassels]


class ImageStack(ee.Image):
    def __init__(self, s1: List[ee.Image] = None, s2: List[ee.Image] = None, dem: list[ee.Image] = None,
                 alos: ee.Image = None, fourier_transform: ee.Image = None):
        self.s1 = s1
        self.s2 = s2 
        self.dem = dem
        self.alos = alos
        self.ft = fourier_transform
        inputs = self.flatten([v for v in self.__dict__.values() if v is not None])
        super().__init__(ee.Image.cat(*inputs), None)
    
    def flatten(self, list_of_lists):
        if len(list_of_lists) == 0:
            return list_of_lists
        if isinstance(list_of_lists[0], list):
            return self.flatten(list_of_lists[0]) + self.flatten(list_of_lists[1:])
        return list_of_lists[:1] + self.flatten(list_of_lists[1:])

# create the inputs
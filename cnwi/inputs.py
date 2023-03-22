from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import Dict, List, Callable, Union

import ee
import tagee

from . import imgs
from . import sfilters
from . import derivatives as driv

from .eelib import eefuncs

import ee
import tagee

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def sentinel1(asset):
    """
    DV = VV + VH
    DH = HH + HV
    SV = VV
    SH = HH
    """
    image = ee.Image(asset)
    if 'DV' in asset or 'SV' in asset:
        image = image.select('V.*')
    elif 'DH' in asset or 'SH' in asset:
        image = image.select('H.*')
    else:
        raise TypeError("Not at Valid Sentinel 1 Asset - id")
    return image


def alos(target_yyyy: int = 2018, aoi: ee.Geometry = None) -> ee.Image:
    alos_collection = ee.ImageCollection("").filterDate(f'{target_yyyy}', f'{target_yyyy + 1}')
    if aoi is not None:
        alos_collection = alos_collection.filterBounds(aoi)
    return alos_collection.mean()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def sentinel2(asset) -> ee.Image:
    return ee.Image(asset).select('B.*')


def data_cube(asset, target_yyyy: int = 2018):
    pass    

    
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

def s2_inputs(assets: list[str]) -> List[ee.Image]:
    # optcial inputs 
    s2s = [sentinel2(_) for _ in assets]
    ndvis = driv.batch_create_ndvi(s2s)
    savis = driv.batch_create_savi(s2s)
    tassels = driv.batch_create_tassel_cap(s2s)

    return [*s2s, *ndvis, *savis, *tassels]


def s1_inputs(assets: list[str], s_filter = None) ->List[ee.Image]:
    # prep the inputs
    s1s = [sentinel1(_) for _ in assets]
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


def elevation_inputs(rectangle: ee.Geometry, image: ee.Image = None, s_filter: Dict[Callable, List[Union[str, int]]] = None):
    image = nasa_dem() if image is None else image
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
        

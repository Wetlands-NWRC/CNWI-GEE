from __future__ import annotations

from dataclasses import dataclass, field, InitVar
from typing import Dict, List, Callable, Union

import ee
import tagee

from . import imgs
from . import sfilters
from . import derivatives as driv

from .eelib import eefuncs


def s2_inputs(assets: list[str]) -> List[ee.Image]:
    # optcial inputs 
    s2s = [imgs.Sentinel2(_) for _ in assets]
    ndvis = driv.batch_create_ndvi(s2s)
    savis = driv.batch_create_savi(s2s)
    tassels = driv.batch_create_tassel_cap(s2s)

    return [*s2s, *ndvis, *savis, *tassels]


def s1_inputs(assets: list[str], s_filter = None) ->List[ee.Image]:
    # prep the inputs
    s1s = [imgs.Sentinel1(_) for _ in assets]
    # sar inputs
    s_filter = sfilters.boxcar(1) if s_filter is None else s_filter
    sar_pp1 = eefuncs.batch_despeckle(s1s, s_filter)
    # sar derivatives
    ratios = driv.batch_create_ratio(
        images=sar_pp1,
        numerator='VV',
        denominator='VH'
    )
    return [*sar_pp1, *ratios]


def elevation_inputs(dem: ee.Image, rectangle: ee.Geometry, s_filter: Dict[Callable, List[Union[str, int]]] = None):
    if s_filter is None:
        s_filter = {
            sfilters.gaussian_filter(3): ['Elevation', 'Slope', 'GaussianCurvature'],
            sfilters.perona_malik(): ['HorizontalCurvature', 'VerticalCurvature', 'MeanCurvature']
        }
    
    out = []
    for filter, selector in s_filter.items():
        smoothed = filter(dem)
        ta = tagee.terrainAnalysis(smoothed, rectangle).select(selector)
        out.append(ta)
        ta, smoothed = None, None
    return out 
        

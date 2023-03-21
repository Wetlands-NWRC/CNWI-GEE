from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field, InitVar
from typing import Dict, List, Callable

import ee
import tagee


from .eelib import eefuncs, sf

@dataclass
class Inputs:
    products: list = field(default_factory=list)


def s2_inputs(assets: list[str]) -> Inputs:
    pass


def s1_inputs(assets: list[str], spatial_filter = None) -> Inputs:
    pass


def elevation_inputs(dem: ee.Image) -> Inputs:
    pass


@dataclass(frozen=True)
class OpticalInputs:
    ee_images: InitVar[list[ee.Image]]
    products:list[ee.Image] = field(default_factory=list)
    def __post_init__(self, ee_images):
        self.products.extend(ee_images)
        self.products.extend(eefuncs.batch_create_ndvi(ee_images))
        self.products.extend(eefuncs.batch_create_savi(ee_images))
        self.products.extend(eefuncs.batch_create_tassel_cap(ee_images))


@dataclass(frozen=True)
class SARInputs:
    ee_images: InitVar[list[ee.Image]]
    s_filter: InitVar
    products: list[ee.Image] = field(default_factory=list)
    def __post_init__(self, ee_images, s_filter):
        pp_1 = eefuncs.batch_despeckle(ee_images, s_filter)
        self.products.extend(pp_1)
        self.products.extend(eefuncs.batch_create_ratio(pp_1, 'VV', 'VH'))


@dataclass(frozen=False)
class DEMInputs:
    ee_image: InitVar[ee.Image]
    rectangle: InitVar[ee.Geometry]
    s_filter: Dict[Callable, List[int]] = field(default_factory=lambda: {sf.gaussian_filter(3): ['Elevation', 'Slope', 'GaussianCurvature'],
                                                                         sf.perona_malik(): ['HorizontalCurvature', 'VerticalCurvature',
                                                                                             'MeanCurvature']})
    products: list[ee.Image] = field(default_factory=list)
    
    def __post_init__(self, ee_image, rectangle):

        for sfilt, selector in self.s_filter.items():
            smoothed = sfilt(ee_image)
            ta = tagee.terrainAnalysis(smoothed, rectangle).select(selector)
            self.products.append(ta)
            ta, smoothed = None, None


@dataclass
class Additional:
    products: list [ee.Image] = field(default_factory=list)
    
    def __len__(self):
        return len(self.products)
    
    def __setitem__(self, _idx, _object):
        self.products[_idx] = _object
    
    def __getitem__(self, key):
        return self.products[key]


def stack(optical_inputs: OpticalInputs, sar_inputs: SARInputs = None, dem_inputs: DEMInputs = None):
    return ee.Image.cat(*optical_inputs.products, *sar_inputs.products, *dem_inputs.products)


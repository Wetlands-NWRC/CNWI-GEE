from __future__ import annotations

from abc import ABC
from dataclasses import dataclass,field, InitVar
from typing import Union, Iterable

import ee
import tagee


from .eelib import eefuncs, sf


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


@dataclass(frozen=True)
class DEMInputs:
    ee_image: InitVar[ee.Image]
    rectangle: InitVar[ee.Geometry]
    s_filter: InitVar[function] = sf.gaussian_filter(3)
    products: list[ee.Image] = field(default_factory=list)
    bands: list[str] = field(default_factory=lambda: [])
    
    def __post_init__(self, ee_image, rectangle, s_filter):
        smoothed = s_filter(ee_image)
        dervi = tagee.terrainAnalysis(smoothed, rectangle).select(['Elevation', 'Slope', 'GaussianCurvature',
                                                                   'HorizontalCurvature', 'VerticalCurvature',
                                                                   'MeanCurvature'])
        self.products.append(dervi)


def stack(optical_inputs: OpticalInputs, sar_inputs: SARInputs = None, dem_inputs: DEMInputs = None):
    return ee.Image.cat(*optical_inputs.products, *sar_inputs.products, *dem_inputs.products)


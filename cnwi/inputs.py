from __future__ import annotations

from abc import ABC
from dataclasses import dataclass,field, InitVar
from typing import Union, Iterable

import ee

from . import funcs

from .datasets import dem
from .datasets import williston

from .eelib import eefuncs, sf


class ImageStack:
    # TODO make sar and dem optional 
    # TODO make more generic
    def __new__(cls, optical: list[ee.Image], sars: list[ee.Image],
                dem: ee.Image, *products: Iterable[ee.Image]) -> ee.Image:
        # apply filtering
        # create derivaitves
        opticals: list[ee.Image] = optical
        
        ndvis = eefuncs.batch_create_ndvi(opticals)
        savis = eefuncs.batch_create_savi(opticals)
        tassels = eefuncs.batch_create_tassel_cap(opticals)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        pp_1 = eefuncs.batch_despeckle(sars, sf.Boxcar(1))
        ratios = eefuncs.batch_create_ratio(pp_1, 'VV', 'VH')
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        elevation = dem.select('elevation')
        slope = ee.Terrain.slope(elevation)
        aspect = ee.Terrain.aspect(elevation)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        return ee.Image.cat(*opticals, *ndvis, *savis, *tassels, *pp_1, *ratios, elevation, slope, 
                            aspect, *products)
    

@dataclass(frozen=False)
class DCWillistonStack64:
    """Williston Datacube Stack Dataclass it is a Pre - Built Dataset for the entires Basin
    
    Products
    --------
    
    - Sentinel - 1 from Orbit Number 64
    - Sentinel - 2 from Data cube
    - DEM - CDEM
    """
    
    viewport: ee.Geometry = InitVar[field(default=None)]
    
    def __post_init__(self, viewport=None):
        seasons = funcs.data_cube_seasons()
        
        if viewport is not None:
            dc_col = williston.WillistonDataCube().filterBounds(viewport)
        else:
            dc_col = williston.WillistonDataCube()    
        
        optical = funcs.parse_season(dc_col.mean(), seasons_dict=seasons)
        
        s1 = funcs.parse_s1_imgs(williston.WillistonS164())
        
        elevation = dem.CDEM(
            viewport=viewport
        )
        
        self.stack = ImageStack(optical=optical, s1=s1, dem=elevation)


@dataclass
class BM_A_WillistonStack:
    """Williston Region A, Bench Mark, contains only gee native datasets
    
    NOTE:
    -----
    
    All products are pre - build list of images
    
    """    
    
    products: InitVar[Iterable[ee.Image]] = None
    
    def __post_init__(self, products):
        
        optical = williston.Williston_A_S2_IL()
        
        s1 = williston.Williston_A_S1_IL()
        
        dem = dem.CDEM(
            viewport=self.viewport
        )
        
        self.stack = ImageStack(optical=optical, s1=s1, dem=dem, *products)


    

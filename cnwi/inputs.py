from __future__ import annotations

from abc import ABC
from dataclasses import dataclass,field, InitVar
from typing import Union, Iterable

import ee

from . import cfg
from . import bands as dc_bands

from .datasets import dem
from .datasets import williston

from .eelib import bands as ee_bands
from .eelib import eefuncs, sf


def parse_season(collection: DataCubeCollection) -> list[ee.Image]:
    CFG = cfg.DataCubeCfg()

    # parse the image into spring summer fall
    s2_sr_bands = [str(_.name) for _ in ee_bands.S2SR]
    # remap the parsed images to Sentinel - 2 SR band mappings
    dc_seas = []
    for sea_cfg in CFG.seasons.values():
        comp = collection.select(sea_cfg.get('band_prefix'))
        start_date = ee.Date(sea_cfg.get('start')).millis()
        end_date = ee.Date(sea_cfg.get('end')).millis()
        comp = comp.set({'system:time_start': start_date, 'system:time_end':
                         end_date})

        comp = comp.select(comp.bandNames(), s2_sr_bands)
        dc_seas.append(comp)
    return dc_seas


def parse_s1_imgs(collection: S1Collection64):
    dates: list[str] = collection.aggregate_array('date').getInfo()
   
    if len(dates) > 3:
        imgs = [collection.filter(f'date == "{date}"').mean().set('date', date)
               for date in sorted(set(dates))]
    else:
        imgs = [ee.Image(_.get('id')).set('date', dates[idx]) for idx, _ 
                in enumerate(collection.toList(collection.size()).getInfo())]

    return imgs


class DataCubeCollection:
    def __new__(cls, asset_id: str, viewport: ee.Geometry = None) -> _DataCubeCollection:
        instance = _DataCubeCollection(asset_id)
        
        if viewport is not None:
            instance = instance.filterBounds(viewport)
        
        src = [ _.name for _ in dc_bands.DataCubeBands]
        dest = [_.value for _ in dc_bands.DataCubeBands]
        return instance.select(src, dest)


class _DataCubeCollection(ee.ImageCollection):
    def __init__(self, args):
        super().__init__(args)


class ImageStack:
    # TODO make sar and dem optional 
    # TODO make more generic
    def __new__(cls, optical: Union[list[str], _DataCubeCollection], 
                s1: Union[list[str], ee.ImageCollection] , dem: ee.Image, *products: Iterable[ee.Image]) -> ee.Image:
        # apply filtering
        # create derivaitves
        if isinstance(optical, _DataCubeCollection):
            opticals: list[ee.Image] = parse_season(optical.mean())
        
        ndvis = eefuncs.batch_create_ndvi(opticals)
        savis = eefuncs.batch_create_savi(opticals)
        tassels = eefuncs.batch_create_tassel_cap(opticals)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        if isinstance(s1, ee.ImageCollection): 
            sars: list[ee.Image] = parse_s1_imgs(s1)
        
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
    
    def __post_init__(self, viewport):
        
        cfg = williston.WillistonDC()
        
        optical = DataCubeCollection(
            asset_id=cfg.assetid,
            viewport=viewport
        )
        
        s1 =  williston.S1Collection64(
            viewport=viewport
        )
        
        dem = dem.CDEM(
            viewport=viewport
        )
        
        self.stack = ImageStack(optical=optical, s1=s1, dem=dem)


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


    

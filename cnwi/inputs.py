from __future__ import annotations

from abc import ABC

import ee

from eelib import stack

import cfg
import bands as dc_bands

from eelib import bands as ee_bands
from eelib import eefuncs, sf


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
    unique_dates = collection.aggregate_array('date').distinct().getInfo()
    
    if len(unique_dates) > 3:
        imgs = [collection.filter(f'date == "{date}"').mean()
               for date in unique_dates]
    else:
        imgs = [ee.Image(_) for _ in collection.toList(collection.size()).getInfo()]

    return imgs


class _Stack(ABC):
    pass


class S1Collection64:
    
    def __new__(cls, viewport: ee.Geometry = None) -> ee.ImageCollection:
        asset_ids = [
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015452_20180609T015517_011290_014BA0_39FD"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015517_20180609T015542_011290_014BA0_2658"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180609T015542_20180609T015616_011290_014BA0_EE30"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015454_20180715T015519_011815_015BE0_0362"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015519_20180715T015544_011815_015BE0_D8D7"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180715T015544_20180715T015618_011815_015BE0_8287"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015503_20180913T015528_012690_0176B4_78B3"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015528_20180913T015553_012690_0176B4_0EB4"
            "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180913T015553_20180913T015613_012690_0176B4_EB44"
        ]
        
        imgs = [ee.Image(_) for _ in asset_ids]
        
        instance = ee.ImageCollection(imgs)
        
        if viewport is not None:
            instance = instance.filterBounds(viewport)

        return instance.map(lambda x: x.set('date', x.date().format('YYYY-MM-dd')))
        

class DataCubeCollection:
    def __new__(cls, asset_id: str, viewport: ee.Geometry = None) -> ee.ImageCollection:
        instance = ee.ImageCollection(asset_id)
        
        if viewport is not None:
            instance = instance.filterBounds(viewport)
        
        src = [ _.name for _ in dc_bands.DataCubeBands]
        dest = [_.value for _ in dc_bands.DataCubeBands]
        return instance.select(src, dest)
    

class DataCubeStack(stack._Stack):
    def __new__(cls, datacubecollection, s1: ee.ImageCollection, dem: ee.Image) -> ee.Image:
        # apply filtering
        # create derivaitves
        
        opticals: list[ee.Image] = parse_season(datacubecollection)
        ndvis = eefuncs.batch_create_ndvi(opticals)
        savis = eefuncs.batch_create_savi(opticals)
        tassels = eefuncs.batch_create_tassel_cap(opticals)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
         
        sars: list[ee.Image] = parse_s1_imgs(s1)
        pp_1 = eefuncs.batch_despeckle(sars, sf.Boxcar(1))
        ratios = eefuncs.batch_create_ratio(pp_1, 'VV', 'VH')
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        elevation = dem.select('elevation')
        slope = ee.Terrain.slope(elevation)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        
        return ee.Image.cat(*opticals, *ndvis, *savis, *tassels, *pp_1, *ratios, elevation, slope)
    

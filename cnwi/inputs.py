from __future__ import annotations

from typing import Dict, List, Callable, Union

import ee
import tagee

from . import sfilters, funcs, bands, imgs
from . import derivatives as driv


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def s2_inputs(assets: list[imgs.Sentinel2]) -> List[ee.Image]:
    if isinstance(assets, imgs.eeDataCube):
        # get seasonal composites, cast to list
        parsed_seasons = assets.get_seasonal_composites()
        index = list(imgs.S2SR.BANDS.keys())
        names = list(imgs.S2SR.BANDS.values())
        s2s = [x.select(index, names) for x in parsed_seasons.values()]
        
    else:
        obj = {
            'S2_HARMONIZED': imgs.S2TOA,
            'S2_SR_HARMONIZED': imgs.S2SR
        }
        s2s = []
        for asset in assets:
            idfer = asset.split("/")[1]
            s2s.append(obj.get(idfer)(asset))
    
    # optcial inputs 
    ndvis = driv.batch_create_ndvi(s2s)
    savis = driv.batch_create_savi(s2s)
    tassels = driv.batch_create_tassel_cap(s2s)

    return [*s2s, *ndvis, *savis, *tassels]


def s1_inputs(assets: list[str], s_filter = None, mosaic: bool = False) ->List[ee.Image]:
    """If mosaic is set to true will return a list containing one image and one ratio
    if set to false will return a list continaing one image for every defined asset and one ration
    for every constructed image
    """
    obj = {
        'DV': imgs.S1DV,
        'DH': imgs.S1DH
    }
    
    spatial_filter = sfilters.boxcar(1) if s_filter is None else s_filter
    
    s1s = []
    for asset in assets:
        name = asset.split("/")[-1].split("_")[3][2:]
        img = obj.get(name)
        s1s.append(img(asset))
    
    #TODO make Sentinel 1 Image Collection
    if mosaic:
        mosaic = ee.ImageCollection(s1s).map(spatial_filter).mosaic()
        ratio = driv.ratio(mosaic, 'VV', 'VH')
        output = [mosaic, ratio]
    else:
        # sar inputs
        s_filter = sfilters.boxcar(1) if s_filter is None else s_filter
        sar_pp1 = [s_filter(_) for _ in s1s]
    
        # sar derivatives
        ratios = driv.batch_create_ratio(
            images=sar_pp1,
            numerator='VV',
            denominator='VH'
        )
        output = [*sar_pp1, *ratios]
    return output


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
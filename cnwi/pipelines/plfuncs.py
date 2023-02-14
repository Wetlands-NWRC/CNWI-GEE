from typing import List, Union

import ee
from eelib import bands, eefuncs, sf

from . import plcfgs


def set_tile_id(element: ee.Image):
    row = ee.Number(element.get('row')).format('%03d')
    col = ee.Number(element.get('col')).format('%03d')
    tile_id = row.cat(col)
    return element.set('tileID', tile_id)


def s1_preprocessing_chain(s1_images: List[ee.Image], filter: sf.SpatialFilter) -> List[ee.Image]:
    # Image Pre processing chain
    s1_images = eefuncs.batch_co_register(
        images=s1_images,
        max_offset=1.0
    )

    s1_images = eefuncs.batch_despeckle(
        images=s1_images,
        filter=filter
    )
    return s1_images


def create_dirv(s1_images: list, s2_images: list) -> list:

    s1_ratio = eefuncs.batch_create_ratio(
        images=s1_images,
        numerator='VV',
        denominator='VH'
    )

    s2_ndiv = eefuncs.batch_create_ndvi(s2_images)
    s2_savi = eefuncs.batch_create_savi(s2_images)
    s2_tc = eefuncs.batch_create_tassel_cap(
        s2_images)

    return [s1_ratio, s2_ndiv, s2_savi, s2_tc]

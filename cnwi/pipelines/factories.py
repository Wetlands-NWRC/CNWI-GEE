from typing import List, Union

import ee
from eelib import bands, eefuncs, sf

from . import plcfgs


class DatacubeCollection:

    def __new__(cls, arg: str) -> ee.ImageCollection:

        def set_tile_id(element: ee.Image):
            row = ee.Number(element.get('row')).format('%03d')
            col = ee.Number(element.get('col')).format('%03d')
            tile_id = row.cat(col)
            return element.set('tileID', tile_id)

        config = plcfgs.DataCubeCfg()

        instance = ee.ImageCollection(arg).map(set_tile_id).\
            select(
                selectors=config.src_bands,
                opt_names=config.dest_bands
        )
        return instance


def datacube_img_factory(datacube_collection: DatacubeCollection,
                         viewport: ee.Geometry = None) -> List[ee.Image]:
    # remap bands to data cube descriptors
    CFG = plcfgs.DataCubeCfg()

    # Convert to Image
    if viewport is not None:
        inputs = datacube_collection.filterBounds(viewport).mosaic()
    else:
        inputs = datacube_collection.mosaic()

    # parse the image into spring summer fall
    s2_sr_bands = [str(_.name) for _ in bands.S2SR]
    # remap the parsed images to Sentinel - 2 SR band mappings
    dc_seas = []
    for sea_cfg in CFG.seasons.values():
        comp = inputs.select(sea_cfg.get('band_prefix'))
        start_date = ee.Date(sea_cfg.get('start')).millis()
        end_date = ee.Date(sea_cfg.get('end')).millis()
        comp = comp.set({'system:time_start': start_date, 'system:time_end':
                         end_date})

        comp = comp.select(comp.bandNames(), s2_sr_bands)
        dc_seas.append(comp)

    return dc_seas


def s1_swath_images(collection: ee.ImageCollection) -> List[ee.Image]:
    """ it  """

    def date_fmt(element: ee.Image):
        return element.set('dateFmt', element.date().format('YYYY-MM-dd'))

    inputs = collection.map(date_fmt)
    unique_dates = inputs.aggregate_array('dateFmt').distinct().getInfo()
    mosaics = [inputs.filter(f'dateFmt == "{date}"').mosaic()
               for date in unique_dates]
    return mosaics


def s1_factory(asset_ids: List[str], selector: Union[str, List[str]] = None):
    selector = 'V.*' if selector is None else selector
    return [ee.Image(id).select(selector) for id in asset_ids]


def s2_factory(asset_ids: List[str], selector: Union[str, List[str]] = None):
    selector = 'B.*' if selector is None else selector
    return [ee.Image(id).select(selector) for id in asset_ids]

from datetime import datetime

import ee

from .datasets.datacube import DataCube
from .datasets.struct import ImageList
from . import bands
from . import td


def parse_season(collection: DataCube, seasons_dict: dict[str, dict[str, str]]) -> list[ee.Image]:
    # parse the image into spring summer fall
    s2_sr_bands = [str(_.name) for _ in bands.S2SR]
    # remap the parsed images to Sentinel - 2 SR band mappings
    dc_seas = []
    for season in seasons_dict.values():
        comp = collection.select(season.get('band_prefix'))
        start_date = ee.Date(season.get('start')).millis()
        end_date = ee.Date(season.get('end')).millis()
        comp = comp.set({'system:time_start': start_date, 'system:time_end':
                         end_date})

        comp = comp.select(comp.bandNames(), s2_sr_bands)
        dc_seas.append(comp)
    return dc_seas


def data_cube_seasons(target_year: int = 2018) -> dict[str, dict[str, str]]:
    def to_datetime(doys: tuple[str]):
        doys = sorted(doys)
        # julain days parse to YYYY MM dd

        def to_dt(doy: int) -> str:
            doy = datetime.strptime(f'{target_year}{doy}', '%Y%j')
            return doy.strftime("%Y-%m-%d")

        return tuple(map(to_dt, doys))

    doys = 135, 181, 182, 243, 244, 300
    dates = to_datetime(doys)
    
    seasons = {
        'spring': {'band_prefix': 'a_spri_b.*', 'start': dates[0], 'end': dates[1]},
        'summer': {'band_prefix': 'b_summ_b.*', 'start': dates[2], 'end': dates[3]},
        'fall': {'band_prefix': 'c_fall_b.*', 'start': dates[4], 'end': dates[5]}
    }
    return seasons


def parse_s1_imgs(collection: ee.ImageCollection):
    dates: list[str] = collection.aggregate_array('date').getInfo()
   
    if len(dates) > 3:
        imgs = [collection.filter(f'date == "{date}"').mean().set('date', date)
               for date in sorted(set(dates))]
    else:
        imgs = [ee.Image(_.get('id')).set('date', dates[idx]) for idx, _ 
                in enumerate(collection.toList(collection.size()).getInfo())]

    return ImageList(imgs)


def generate_samples(stack: ee.Image, training_data: td.TrainingData, scale: int = 10,
                     projection = None, tile_scale: int = 16, geom: bool = False) -> Union[TrainingData, ee.FeatureCollection]:
    # TODO move to funcs, make so that will return a feature collection, if TD passes will returned an updated training data object
    ee_lookup = ee.Dictionary(training_data.labels)
    
    def insert_value(element: ee.Feature):
        return element.set(training_data.value, ee_lookup.get(element.get(training_data.label)))
    
    def add_geometry(element: ee.Feature):
        x,y = element.get('POINT_X'), element.get('POINT_Y')
        return ee.Feature(ee.Geometry.Point([x, y])).copyProperties(element)
    
    to_sample = training_data.collection if isinstance(training_data, td.TrainingData)\
        else training_data
    
    samples = stack.sampleRegions(
        collection = to_sample,
        properties = [training_data.value, training_data.label, 'POINT_X', 'POINT_Y'],
        scale = scale,
        projection = projection,
        tileScale = tile_scale,
        geometries = geom
    ).map(insert_value).map(add_geometry)
    
    training_data.samples = samples
    
    return training_data
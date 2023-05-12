from typing import List, Union

import ee
from cnwi import opt, rf, sar, trainingd
from cnwi import derivatives as d
from cnwi import sfilters as s


def build_data_cube(arg: str, aoi: ee.Geometry) -> ee.Image:
    # need to prep the datacube 
    """ Handles building data cube collection that can be used downstream """
    
    # construct a base data cube object and filter by the aoi
    col = opt.DataCubeComposite(arg).filter(aoi)
    
    band_prefixs = col.show_band_prefix()
    band_names = col.show_band_names()
    # remove the 60m band
    remove_60 = [i for i in band_names.values() if '60m' not in i]
    band_selc = {k: [_ for _ in remove_60 if k in _] for k in band_prefixs.values()}
    # select by the prefix, then remove any strings that have 60m in it
    names = band_selc.pop('a_spri_b')
    for val in band_selc.values():
        names = names + val
    
    # Standardize band names to S2 
    s2_names = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']

    ## Remapping Band Names to s2 standard
    spring_new = s2_names
    summer_new = [f'{_}_1' for _ in s2_names]
    fall_new = [f'{_}_2' for _ in s2_names]
    
    new_band_names = spring_new + summer_new + fall_new
    
    col.map(lambda x: x.select(names, new_band_names))
    
    # create the objects to be mapped
    
    ##NDVI
    spring_NDVI = d.NDVI()
    summer_NDVI = d.NDVI(nir='B8_1', red='B4_1')
    fall_NDVI = d.NDVI(nir='B8_2', red='B4_2')
    
    ##SAVI
    spring_SAVI = d.SAVI()
    summer_SAVI = d.SAVI(nir='B8_1', red='B4_1')
    fall_SAVI = d.SAVI(nir='B8_2', red='B4_2')

    ##Tassel Cap
    spring_tc = d.TasselCap()
    summer_tc = d.TasselCap(
        blue="B2_1",
        red='B4_1',
        green='B3_1',
        nir='B8_1',
        swir_1='B11_1',
        swir_2='B12_1'
    )

    fall_tc = d.TasselCap(
        blue="B2_2",
        red='B4_2',
        green='B3_2',
        nir='B8_2',
        swir_1='B11_2',
        swir_2='B12_2'
    )
    
    return col.map(spring_NDVI).map(summer_NDVI).map(fall_NDVI).map(spring_SAVI).map(summer_SAVI).\
        map(fall_SAVI).map(spring_tc).map(summer_tc).map(fall_tc).mosaic()


def build_sentinel1(col: ee.ImageCollection):
    EARLY_SEASON = '2019-04-01', '2019-06-20'
    LATE_SEASON = '2019-06-21', '2019-10-31'
    
    # select only VV and VH
    in_col = col.select('V.*')
    # apply spatial filter
    boxcarf = s.boxcar(1)
    s1_pp1 = in_col.map(boxcarf)
    # add ratio
    ratio = d.Ratio('VV', 'VH')
    s1_pp2 = s1_pp1.map(ratio)
    # sperate into early and late season
    early = s1_pp2.filterDate(*EARLY_SEASON)
    late = s1_pp2.filterDate(*LATE_SEASON)
    # mosaic early and late
    early_mosaic = early.mosaic()
    late_mosaic = late.mosaic()
    # concat early and late into one image
    return ee.Image.cat(early_mosaic, late_mosaic)


def build_alos(target_year: int = 2019) -> ee.Image:
    # build alos mosaic
    mosaic: ee.Image = sar.ALOS().filterDate(f'{target_year}', f'{target_year + 1}')\
        .select('H.*').first()
    
    # Create a Ratio Calc obj
    ratio = d.Ratio(
        numerator='HH',
        denominator='HV'
    )
    
    # add the ratio band to the mosaic
    with_ratio = ratio.calculate(mosaic)
    return with_ratio


def build_elevation(arg: str, aoi: ee.Geometry = None) -> ee.Image:
    """ pre computed dataset """
    col = ee.ImageCollection(arg)
    
    if aoi is not None:
        return col.filterBounds(aoi).mosaic()
    else:
        return col.mosaic()


def build_fourier_transform(arg: str, aoi: ee.Geometry = None) -> ee.Image:
    """ pre computed dataset """
    col = ee.ImageCollection(arg)
    
    if aoi is not None:
        return col.filterBounds(aoi).mosaic()
    else:
        return col.mosaic()


def build_stack(*images) -> ee.Image:
    return ee.Image.cat(*images)


def training_data_set(stack: ee.Image, table: ee.FeatureCollection, label_col: str) -> ee.FeatureCollection:
    # prep the input training points
    preped = trainingd.prep_training_data(
        col=table,
        class_property=label_col
    )
    
    samples = trainingd.generate_samples(
        stack=stack,
        col=preped
    )
    
    return samples


# build_rf_model
def build_random_forest_model(number_of_trees: int = 1000) -> rf.RandomForestModel:
    # TODO look into putting constraints on how the model can grow
    return rf.RandomForestModel(
        numberOfTrees=number_of_trees
    )


def train_random_forest_model(model: rf.RandomForestModel, training_data, predictors: Union[List[str], ee.List], classProperty: str):
    return model.train()


# classify_stack
def classify_stack(trained_model, stack: ee.Image) -> ee.Image:
    return stack.classify(trained_model).uint8()


def do_accuracy_assessment() -> ee.FeatureCollection:
    pass
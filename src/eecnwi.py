import ee
from cnwi import opt
from cnwi import derivatives as d


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


def build_sentinel1(args: List[str]):
    pass


def build_alos():
    pass


def build_elevation(arg: str):
    """ pre computed dataset """
    pass


def build_fourier_transform(arg: str):
    """ pre computed dataset """
    pass


def build_stack(*images) -> ee.Image:
    return ee.Image.cat(*images)


# need training

# build_rf_model

# classify_stack


import ee

from . import derivatives as d


def prep_data_cube(col: ee.ImageCollection):
    """ Handles building data cube collection that can be used downstream """
    # Standardize band names to S2 
    s2_names = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
    
    # input
    first = col.first()
    
    ## Spring Bands
    spring_prefix = 'a_spri_b.*'
    spring_bands: ee.List = first.select(spring_prefix).bandNames()
    
    ## Summer Bands
    summer_prefix = 'b_summ_b.*'
    summer_bands: ee.List = first.select(summer_prefix).bandNames()
    
    ## Fall Bands
    fall_prefix = 'c_fall_b.*'
    fall_bands: ee.List = first.select(fall_prefix).bandNames()

    # cat bands, selection 
    concat = spring_bands.cat(summer_bands).cat(fall_bands)
    
    ## Remapping Band Names to s2 standard
    spring_new = s2_names
    summer_new = [f'{_}_1' for _ in s2_names]
    fall_new = [f'{_}_2' for _ in s2_names]
    
    new_band_names = spring_new + summer_new + fall_new
    
    return col.map(lambda x: x.select(concat, new_band_names))


def build_data_cube_inpts(col: ee.ImageCollection)-> ee.Image:
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
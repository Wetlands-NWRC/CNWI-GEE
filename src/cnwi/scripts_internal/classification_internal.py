import ee

import eecnwi
from cnwi.rf import RandomForestModel

def run(aoi: ee.Geometry, training_data: str, opt:str, fourier: str, elevation:str) -> ee.Image:
    """ Does bare bones classification """
    
    # Sentinel -1 
    opt = eecnwi.build_data_cube(
        arg=opt,
        aoi=aoi
    )
    
    sar = eecnwi.build_sentinel1(
        aoi=aoi
    )
    
    alos = eecnwi.build_alos()
    
    ft = eecnwi.build_fourier_transform(
        arg=fourier,
        aoi=aoi
    )
    
    elev = eecnwi.build_elevation(elevation, aoi=aoi)
    
    stack = ee.Image.cat(opt, sar, alos, ft, elev)
    
    samples = stack.sampleRegions(
        collection=training_data,
        scale=10,
        tileScale=16
    )
    
    clf = RandomForestModel()
    
    clf_trained = clf.train()
    
    
    
    
    
    
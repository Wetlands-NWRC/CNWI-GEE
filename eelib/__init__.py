import ee

from . import eefactory

if not ee.data._credentials:
    ee.Initialize()

# add class factory methods to ee.ImageCollection and ee.FeatureCollection
fc_base = ee.FeatureCollection

fc_base.from_dataframe = eefactory.from_dataframe
fc_base.from_file = eefactory.from_file
fc_base.from_image_collection = eefactory.from_image_collection
fc_base.to_file = eefactory.to_file

# Image Collection Factory class methods
ic_base = ee.ImageCollection
ic_base.s1Collection = eefactory.s1Collection
ic_base.s2TOACollection = eefactory.s2TOACollection
ic_base.s2SRCollection = eefactory.s2SRCollection

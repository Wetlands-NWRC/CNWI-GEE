import ee
import td


def datacubelogging(image_collection: ee.ImageCollection) -> ee.FeatureCollection:
    # map the tile id to the tile
    # get the geometry 
    # dc = image_collection.map(lambda x: x.set('tile_id': ee.St))
    pass


def sentinel1logging(image_collection: ee.ImageCollection) -> ee.FeatureCollection:
    as_list = image_collection.toList(image_collection.size())
    
    response = as_list.getInfo()
    features: list[dict] = []
    for obj in response:
        geom = obj.get('system:footprint', None)
        props = {
            "system_index": obj.get('id') 
        }
        features.append(ee.Feature(geom=geom, opt_properties=props))

    return ee.FeatureCollection(features)


def predictors_log(bandNames: ee.List) -> ee.FeatureCollection:
    def func(element):
            return ee.Feature(None, {'predictor': element})

    return ee.FeatureCollection(bandNames.map(func))


def training_data_log(training_data: td.TrainingData) -> ee.FeatureCollection:
    if training_data.samples is None:
        raise Exception("TrainingData.samples is None, cannot create feature collection")
    
    labels = training_data.samples.aggregate_array(training_data.label).distinct()
    values = training_data.samples.aggregate_array(training_data.value).distinct()
    counts = labels.map(lambda x: training_data.samples\
        .filter(ee.Filter.eq(training_data.label, x)).aggregate_count(training_data.label))
    
    features: list[ee.Feature] = []
    for idx, _ in enumerate(labels.getInfo()):
        geom = None
        props = {
            'label': labels.get(idx),
            'value': values.get(idx), 
            'count': counts.get(idx)
        }
        feature = ee.Feature(geom, props)
        features.append(feature)
    
    return ee.FeatureCollection(features)
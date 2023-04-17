import ee


def validation(validation_set: ee.FeatureCollection, model, class_property: str) -> ee.FeatureCollection:
    """ used to do validation """
    validated = validation_set.classify(model)
    base = validated.errorMatrix(class_property, 'classification')
    cfm = ee.Feature(None, {'confusion_matrix': base})
    overall = ee.Feature(None, {'overall': base.accuracy()})
    producers = ee.FeatureCollection(None, {'producers': base.producersAccuracy()})
    consumers = ee.FeatureCollection(None, {'consumers': base.consumersAccuracy()})
    return ee.FeatureCollection([cfm, overall, producers, consumers])
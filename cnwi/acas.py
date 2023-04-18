import ee
import pandas as pd


def validation(validation_set: ee.FeatureCollection, model, class_property: str) -> ee.FeatureCollection:
    """ used to do validation """
    validated = validation_set.classify(model)
    base = validated.errorMatrix(class_property, 'classification')
    cfm = ee.Feature(None, {'confusion_matrix': base})
    overall = ee.Feature(None, {'overall': base.accuracy()})
    producers = ee.FeatureCollection(None, {'producers': base.producersAccuracy()})
    consumers = ee.FeatureCollection(None, {'consumers': base.consumersAccuracy()})
    return ee.FeatureCollection([cfm, overall, producers, consumers])


class ConfusionMatrix(pd.DataFrame):
    def __init__(self, ee_confusion_max, labels: list) -> None:
        """ Constucts a Pandas Dataframe that represents  a confusion matrix"""
        data = ee_confusion_max.array().slice(0,1).slice(1,1)
        super().__init__(data=data, index=labels, columns=labels)


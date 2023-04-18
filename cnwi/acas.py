import json
from typing import Dict

import ee
import pandas as pd

from . import table


def validation(validation_set: ee.FeatureCollection, model, class_property: str) -> ee.FeatureCollection:
    """ used to do validation """
    validated = validation_set.classify(model)    
    base = validated.errorMatrix(class_property, 'classification')
    order = ee.Feature(None, {"order": base.order().slice(1)})
    cfm = ee.Feature(None, {'confusion_matrix': base.array().slice(0,1).slice(1,1)})
    overall = ee.Feature(None, {'overall': base.accuracy()})
    producers = ee.Feature(None, {'producers': base.producersAccuracy()})
    consumers = ee.Feature(None, {'consumers': base.consumersAccuracy()})
    return ee.FeatureCollection([order, cfm, overall, producers, consumers])


class eeValidator:
    def __init__(self, val_sample: table.Sample, model, class_prop: str = None, label_col: str =None) -> None:
        self.label_col = 'land_cover' if label_col is None else label_col
        self.class_prop = 'value' if class_prop is None else class_prop
        
        self._cfm = self._get_confusion_matrix(
            val_sample=val_sample,
            model=model,
            class_prop=self.class_prop
        )
        
        self.cfm = ee.Feature(None, {'confusion_matrix': self._cfm.array().slice(0,1).slice(1,1)})
        self.order = ee.Feature(None, {"order": self._cfm.order().slice(1)})
        self.labels = ee.Feature(None, {"labels": self._get_labels(val_sample, self.class_prop, 
                                                                  self.label_col)})
        self.overall = ee.Feature(None, {'overall': self._cfm.accuracy()})
        self.producers = ee.Feature(None, {'producers': self._cfm.producersAccuracy().toList()\
            .flatten().slice(1)})
        self.consumers = ee.Feature(None, {'consumers': self._cfm.consumersAccuracy().toList()\
            .flatten().slice(1)})
    # Helper functions
    def _get_confusion_matrix(self, val_sample, model, class_prop):
        validated = val_sample.classify(model)    
        return validated.errorMatrix(class_prop, 'classification')
    
    def _get_labels(self, samples, class_prop, labels):
        def mapper(element):
            filter = ee.Filter.eq(class_prop, element)
            return samples.filter(filter).aggregate_array(labels).distinct()
        return ee.List(self.order.get('order')).map(mapper).flatten()

    def as_collection(self):
        return ee.FeatureCollection([self.cfm, self.order, self.labels, self.overall,
                                     self.producers, self.consumers])

class ConfusionMatrix(pd.DataFrame):
    def __init__(self, ee_confusion_max, labels: list) -> None:
        """ Constucts a Pandas Dataframe that represents  a confusion matrix from a 
        ee.ConfusionMatrix"""
        data = ee_confusion_max.array().slice(0,1).slice(1,1)
        super().__init__(data=data, index=labels, columns=labels)


class FormatMetrics:
    def __init__(self, filename) -> None:
        with open(filename) as f:
            geo = json.load(f)

        feature = geo['features']
        props = [_.get('properties') for _ in feature]
        self.data = {k: v for _ in props for k,v in _.items()}
    
    def get_confusion(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=self.data.get('confusion_matrix'),
            columns=self.data.get('labels'),
            index=self.data.get('labels')
        )
    
    def get_consumers(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=[self.data.get('consumers')],
            columns=self.data.get('labels'),
            index=['consumers']
        )
    
    def get_producers(self) -> pd.DataFrame:
        return pd.DataFrame(
            data=[self.data.get('producers')],
            columns=self.data.get('labels'),
            index=['producers']
        )
    
    def get_overall(self) -> float:
        pass
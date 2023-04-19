from __future__ import annotations

import json
from typing import Union, Dict, Any

import ee
import pandas as pd

from . import table


class eeValidator: 
    
    def __init__(self, val_sample: Union[table.Sample, ee.FeatureCollection], model: "ee.Classifier", 
                 class_prop: str = None, label_col: str =None) -> None:
        """A tool for doing independent validation in Google Earth Engine
        
        The tool extracts: 
        - confusion Matrix
        - order of the labels
        - the labels i.e. bog, fen etc...
        - overall accuracy
        - producers accuracy
        - consumers accuracy
        
        Args:
            val_sample (Union[table.Sample, ee.FeatureCollection]): the sample used for independent Validation
            model (ee.Classifier): the ee Classifier you wish to validate
            class_prop (str, optional): The name of the property containing the class integer. 
                Each feature must have this property. Defaults to value.
            label_col (str, optional): The name of the property containing the class string.
                Each feature must have this property. Defaults to land_cover.
        """        

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
    def _get_confusion_matrix(self, val_sample, model, class_prop) -> "ee.ConfusionMatrix":
        """ helper function to extract the confusion matrix """
        validated = val_sample.classify(model)    
        return validated.errorMatrix(class_prop, 'classification')
    
    def _get_labels(self, samples, class_prop, labels) -> ee.List:
        """ extracts the values for the class property that represents the class string """
        def mapper(element):
            filter = ee.Filter.eq(class_prop, element)
            return samples.filter(filter).aggregate_array(labels).distinct()
        return ee.List(self.order.get('order')).map(mapper).flatten()

    def as_collection(self) -> ee.FeatureCollection:
        """Containerizes:
            - confusion Matrix
            - order of the labels
            - the labels i.e. bog, fen etc...
            - overall accuracy
            - producers accuracy
            - consumers accuracy

        is meant to be used for when you'd like to export to external storage i.e. drive or
        cloud storage 
        
        Returns:
            ee.FeatureCollection: the containerized metrics
        """        
        return ee.FeatureCollection([self.cfm, self.order, self.labels, self.overall,
                                     self.producers, self.consumers])


class eeConfusionMatrix(pd.DataFrame):
    def __init__(self, ee_confusion_max, labels: list) -> None:
        """ Constucts a Pandas Dataframe that represents  a confusion matrix from a 
        ee.ConfusionMatrix"""
        data = ee_confusion_max.array().slice(0,1).slice(1,1)
        super().__init__(data=data, index=labels, columns=labels)


class FormatMetrics:
    def __init__(self, filename: str) -> None:
        """A helper class that Is used to format the exported results from eeValidator Class. It
        takes in a geojson file that has been exported from Google earth engine and converts the 
        derived data into Pandas.Dataframes 

        Args:
            filename (str): a string that represents a path to the input geojson
        """        
        with open(filename) as f:
            geo = json.load(f)

        feature = geo['features']
        props = [_.get('properties') for _ in feature]
        self.data = {k: v for _ in props for k,v in _.items()}
    
    def get_confusion(self) -> pd.DataFrame:
        """ Converts the  """
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


class _DFMetics(pd.DataFrame):
    
    def _get_features(self, data: Dict[str, Any]):
        feature = data['features']
        props = [_.get('properties') for _ in feature]
        self.data = {k: v for _ in props for k,v in _.items()}


class ConfusionMatrix(_DFMetics):
    def __init__(self, data: Dict[str, Any]) -> None:
        self._get_features(data)
        df = pd.DataFrame(
            data=self.data.get('confusion_matrix'),
            columns=self.data.get('labels'),
            index=self.data.get('labels')
        )
        super().__init__(df)


class Consumers(_DFMetics):
    def __init__(self, data: Dict[str, Any]) -> None:
        self._get_features(data)
        df = pd.DataFrame(
            data=[self.data.get('consumers')],
            columns=self.data.get('labels'),
            index=['consumers']
        )
        super().__init__(df)


class Producers(_DFMetics):
    def __init__(self, data: Dict[str, Any]) -> None:
        self._get_features(data)
        df = pd.DataFrame(
            data=[self.data.get('producers')],
            columns=self.data.get('labels'),
            index=['producers']
        )
        super().__init__(df)
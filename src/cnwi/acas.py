import os
import json
from typing import Dict, Any, List

import ee
import pandas as pd


def _generate_metrics(cfm, order, labels) -> List[ee.Feature]:
    fcfm = ee.Feature(None, {'confusion_matrix': cfm.array().slice(0,1).slice(1,1)})
    order = ee.Feature(None, {"order": order})
    overall = ee.Feature(None, {'overall': cfm.accuracy()})
    producers = ee.Feature(None, {'producers': cfm.producersAccuracy().toList()\
        .flatten().slice(1)})
    consumers = ee.Feature(None, {'consumers': cfm.consumersAccuracy().toList()\
        .flatten().slice(1)})
    labels = ee.Feature(None, {"labels": labels})
    return [fcfm, order, overall, producers, consumers, labels]


def _get_labels(order, samples, class_prop, labels) -> ee.List:
    """ extracts the values for the class property that represents the class string """
    def mapper(element):
        filter = ee.Filter.eq(class_prop, element)
        return samples.filter(filter).aggregate_array(labels).distinct()
    return ee.List(order).map(mapper).flatten()


def out_of_bag(confusion_matrix, label: str):
    raise NotImplementedError


def independent(sample: ee.FeatureCollection, model, class_property: str, label: str) -> ee.FeatureCollection:   
    """ helper function to extract the confusion matrix """
    validated = sample.classify(model)    
    cfm = validated.errorMatrix(class_property, 'classification')
    
    order = cfm.order().slice(1)
    labels = _get_labels(
        order=order,
        samples=sample,
        class_prop=class_property,
        labels=label
    )
    
    metrics = _generate_metrics(cfm, order=order, labels=labels)
    return ee.FeatureCollection(metrics)


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


def _get_features(data: Dict[str, Any]):
    feature = data['features']
    props = [_.get('properties') for _ in feature]
    return {k: v for _ in props for k,v in _.items()}


class ConfusionMatrix(pd.DataFrame):
    def __init__(self, data: Dict[str, Any]) -> None:
        feats = _get_features(data)
        data=feats.get('confusion_matrix')
        columns=feats.get('labels')
        index=feats.get('labels')
        super().__init__(data=data, columns=columns, index=index)


class Consumers(pd.DataFrame):
    def __init__(self, data: Dict[str, Any]) -> None:
        feats = _get_features(data)
        data=[feats.get('consumers')],
        columns=feats.get('labels'),
        index=['consumers']
        super().__init__(data=data, columns=columns, index=index)


class Producers(pd.DataFrame):
    def __init__(self, data: Dict[str, Any]) -> None:
        feats =_get_features(data)
        data=[feats.get('producers')],
        columns=feats.get('labels'),
        index=['producers']
        super().__init__(data=data, columns=columns, index=index)


class Overall(pd.DataFrame):
    def __init__(self, data) -> None:
        feats = _get_features(data)
        data=[feats.get('overall')]
        columns=['Overall']
        super().__init__(data=data, columns=columns)


def metric_tables_to_csv(infile: str, outdir: str, confusion_n: str = None, producers_n: str = None,
                        consumers_n: str = None, overall_n: str = None) -> None:
    """
    infile: represents the geojson outputed from google earth enigne
    
    out dir represents where you would like to write metrics to
    """
    
    consumers_n = 'confusion_matrix.csv' if consumers_n is None else consumers_n
    producers_n = 'confusion_matrix.csv' if producers_n is None else producers_n
    overall_n = 'confusion_matrix.csv' if overall_n is None else overall_n
    confusion_n = 'confusion_matrix.csv' if confusion_n is None else confusion_n
    
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    with open(infile) as f:
        data = json.load(f)
    
    ConfusionMatrix(data).to_csv(os.path.join(outdir, confusion_n))
    Consumers(data).to_csv(os.path.join(outdir, consumers_n))
    Producers(data).to_csv(os.path.join(outdir, producers_n))
    Overall(data).to_csv(os.path.join(outdir, overall_n))
    return None
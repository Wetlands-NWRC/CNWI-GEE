import csv
import json
from typing import Tuple, List
import ee


def _insert_xy(element: ee.Feature):
    coords = element.geometry().coordinates()
    x = coords.get(0)
    y = coords.get(1)
    return element.set({'POINT_X': x, 'POINT_Y': y})


def prep_training_data(col: ee.FeatureCollection, class_property: str = None) -> ee.FeatureCollection:
    """Used to prep the training data for downstream sampling. Adds the Point Geometry, in x,y to the 
    collection as well adds a random colum with values distributed from 0 - 1.
    
    if the class property is specified it will remap the column to an interger values that 
    represent the unique classes in alphabetical order or will remap values to an ordered 
    sequence starting at 1 to n. 

    Args:
        col (ee.FeatureCollection): collection to prep
        class_property (str, optional): class column to remap to interger. Defaults to None.

    Returns:
        ee.FeatureCollection: a feature collection that has been preped for downstream use
    """    
    # add corrdinates
    if class_property is not None:
        classes = col.aggregate_array(class_property).distinct().sort()
        values = ee.List.sequence(1, classes.size())
        lookup = ee.Dictionary.fromLists(classes, values)
        col = col.map(lambda x: x.set('value', lookup.get(x.get(class_property))))
    # add randomColumn
    return col.map(_insert_xy)


def generate_samples(col: ee.FeatureCollection, stack: ee.Image, scale: int = 10, 
                     tile_scale: int = 16, properties: List[str] = None) -> ee.FeatureCollection:
    """ Generates samples off the input collection and stack
    Returns:
        ee.FeatureCollection: a geometryless feature collection
    """
    
    sample = stack.sampleRegions(**{
        'collection': col,
        'scale': scale,
        'tileScale': tile_scale,
        'properties': properties if properties is not None else None,
    })

    return sample


def partition_training(col: ee.FeatureCollection, partition: float) -> Tuple[ee.FeatureCollection]:
    """used to split a single dataset into training and validation.

    Args:
        col (ee.FeatureCollection): the collection to partition
        partition (float): number to split on must be between 0 and 1

    Returns:
        Tuple[ee.FeatureCollection]: training, validation
    """    
    col = col.randomColumn()
    training = col.filter(f'random <= {partition}')
    validation = col.filter(f'random > {partition}')
    return training, validation


def fc_from_file(filename: str) -> ee.FeatureCollection:
    def _read_csv(filename) -> List[ee.Feature]:
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            features = [ee.Feature(None, row) for row in reader]
        return features
    
    def _read_geojson(filename) -> List[ee.Feature]:
        with open(filename) as f:
            data = json.load(f)
        
        return [ee.Feature(None, _['properties']) for _ in data['features']]
    
    codecs = {
        'csv': _read_csv,
        'geojson': _read_geojson
    }
    
    ext = filename.split(".")[-1]
    
    writer = codecs.get(ext, None)
    
    if writer is None:
        raise ValueError("File Not supported")
    
    return ee.FeatureCollection(writer)

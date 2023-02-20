from __future__ import annotations

from dataclasses import dataclass, field

import ee

from .eelib import eefuncs


@dataclass
class TrainingData:
    collection: ee.FeatureCollection
    label: str = field(default="land_cover")
    value: str = field(default='value')
    samples: ee.FeatureCollection = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        self.collection = self.collection.map(eefuncs.add_xy_property)
        
    @property
    def headers(self) -> list[str]:
        properties = self.collection.first().getInfo().get('properties')
        return list(properties.keys())

    @property    
    def labels(self) -> dict[int, str]:
        if self.label not in self.headers:
            raise LookupError(f"{self.label} not in headers")
    
        labels = self.collection.aggregate_array(self.label).distinct().sort().getInfo()
        return {lbl: value for value, lbl in enumerate(labels, start=1)}


def generate_samples(stack: ee.Image, training_data: TrainingData, scale: int = 10,
                     projection = None, tile_scale: int = 16, geom: bool = False) -> TrainingData:
    
    ee_lookup = ee.Dictionary(training_data.labels)
    
    def insert_value(element: ee.Feature):
        return element.set(training_data.value, ee_lookup.get(element.get(training_data.label)))
    
    def add_geometry(element: ee.Feature):
        x,y = element.get('POINT_X'), element.get('POINT_Y')
        return ee.Feature(ee.Geometry.Point([x, y])).copyProperties(element)
    
    samples = stack.sampleRegions(
        collection = training_data.collection,
        properties = [training_data.value, training_data.label, 'POINT_X', 'POINT_Y'],
        scale = scale,
        projection = projection,
        tileScale = tile_scale,
        geometries = geom
    ).map(insert_value).map(add_geometry)
    
    training_data.samples = samples
    
    return training_data
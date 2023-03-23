from __future__ import annotations

from dataclasses import dataclass, field
import ee

from . import funcs

@dataclass
class TrainingData:
    collection: ee.FeatureCollection
    label: str = field(default="land_cover")
    value: str = field(default='value')
    samples: ee.FeatureCollection = field(default=None, init=False, repr=False)
    properties: list = field(default_factory= lambda : ['land_cover', 'value', 'POINT_X', 'POINT_Y'], init=False, repr=False)
    
    def __post_init__(self):
        
        labels: ee.List = self.collection.aggregate_array(self.label).distinct().sort()
        values: ee.List = ee.List.sequence(1, labels.size())
        ee_lookup = ee.Dictionary.fromLists(labels, values)
        
        self.collection = self.collection.map(funcs.add_xy_property)\
            .map(self._standardize(self.label, ee_lookup))

    def _standardize(self, column, lookup) -> callable:
        def wrapper(element: ee.Feature):
            key = element.get(column)
            new = element.set({
                'land_cover': ee.String(key).toLowerCase(),
                'value': lookup.get(key) 
            })
            return new.select(self.properties)
        return wrapper

    def sample(self, stack: ee.Image, scale: int = 10, projection = None, tile_scale: int = 16,
               geom: bool = False) -> None:
        samples = stack.sampleRegions(
            collection = self.collection,
            scale = scale,
            projection = projection,
            tileScale = tile_scale,
            geometries = geom
        )
        self.samples = samples
        return None
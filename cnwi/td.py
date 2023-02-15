from __future__ import annotations

from dataclasses import dataclass, field

import ee

from eelib import eefuncs

@dataclass
class TrainingData:
    collection: ee.FeatureCollection
    label: str = field(default="land_cover")
    value: str = field(default='value')
    samples: str = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        self.collection = self.collection.map(eefuncs.add_xy_property)
    
    #TODO create sample config / expose sampling arguments to user
    def generate_samples(self, stack: ee.Image) -> None:
        self.samples = stack.sampleRegions(
            collection = self.collection,
            properties = None,
            scale = 10,
            projection = None,
            tileScale = None,
            geometries = False
        )
        return None
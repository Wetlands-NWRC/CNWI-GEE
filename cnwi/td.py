from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

import geopandas as gpd
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

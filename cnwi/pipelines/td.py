from __future__ import annotations

from dataclasses import dataclass, field

import ee

@dataclass
class TrainingData:
    collection: ee.FeatureCollection
    label: str = field(default="land_cover")
    value: str = field(default='value')
    samples: str = field(default=None, init=False, repr=False)
    
    #TODO create sample config / expose sampling arguments to user
    def generate_samples(self, stack: ee.Image) -> None:
        self.samples = stack.sampleRegions(
            
        )
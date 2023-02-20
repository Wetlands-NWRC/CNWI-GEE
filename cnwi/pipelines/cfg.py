from __future__ import annotations

from dataclasses import dataclass, field

import ee
from eelib import stack

import td


@dataclass
class RandomForestCFG:
    stack: stack._Stack
    training_data: td.TrainingData
    n_trees: int = 1000
    var_per_split: int = None
    min_leaf: int = 1
    bag_fraction: float = 0.5
    max_nodes: int = None
    seed: int = 0
    mode: str = field(default="CLASSIFICATION")
    predictors: list[str] = field(default_factory=list)
    
    def __post_init__(self):
        _valid_modes = ['CLASSIFICATION', 'PROBABILITY', 'REGRESSION']
        in_mode = self.mode.upper()
        if in_mode not in _valid_modes:
            raise TypeError(f"{self.mode} is not a valid mode")
        else:
            self.mode = in_mode
        
        
@dataclass
class RFModel:
    model: "ee.Classifier"
    classified: ee.Image
    samples: ee.FeatureCollection
    
    
from __future__ import annotations

from dataclasses import dataclass, field

import td


@dataclass
class RandomForestCFG:
    training_data: td.TrainingData
    n_trees: int = 1000
    var_per_split: int = None
    min_leaf: int = 1
    bag_fraction: float = 0.5
    max_nodes: int = None
    seed: int = 0
    mode: str = field(default="CLASSIFICATION")
    
    def __post_init__(self):
        _valid_modes = ['CLASSIFICATION', 'PROBABILITY', 'REGRESSION']
        in_mode = self.mode.upper()
        if in_mode not in _valid_modes:
            raise TypeError(f"{self.mode} is not a valid mode")
        else:
            self.mode = in_mode

    
    
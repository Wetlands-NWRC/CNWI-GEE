from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from datetime import datetime

import ee

import td
import bands as dc_bands


@dataclass
class DataCubeCfg:
    target_year: int = 2018
    doys: InitVar[tuple] = 135, 181, 182, 243, 244, 300
    band_prefix = {'spring': 'a_spri_b.*', 'summer': 'b_summ_b.*',
                   'fall': 'c_fall_b.*'}

    def __post_init__(self, doys):
        def to_datetime(doys: tuple[str]):
            doys = sorted(doys)
            # julain days parse to YYYY MM dd

            def to_dt(doy: int) -> str:
                doy = datetime.strptime(f'{self.target_year}{doy}', '%Y%j')
                return doy.strftime("%Y-%m-%d")

            return tuple(map(to_dt, doys))

        dates = to_datetime(doys)

        self.seasons = {
            'spring': {'band_prefix': 'a_spri_b.*', 'start': dates[0], 'end': dates[1]},
            'summer': {'band_prefix': 'b_summ_b.*', 'start': dates[2], 'end': dates[3]},
            'fall': {'band_prefix': 'c_fall_b.*', 'start': dates[4], 'end': dates[5]}
        }

        self.src_bands = [str(_.name) for _ in dc_bands.DataCubeBands]
        self.dest_bands = [str(_.value) for _ in dc_bands.DataCubeBands]


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
        
    
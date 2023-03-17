from __future__ import annotations
from dataclasses import dataclass, field

import ee

from . import td

from .eelib import classifiers as rf

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
        
        if not self.predictors:
            self.predictors = self.stack.bandNames()
        

@dataclass(frozen=True)
class RFOutput:
    model: "ee.Classifier"
    classified: ee.Image
    samples: ee.FeatureCollection


def cnwi_random_forest(config: RandomForestCFG) -> RFOutput:
    model = rf.RandomForest(
        n_trees=config.n_trees,
        var_per_split=config.var_per_split,
        min_leaf_pop=config.min_leaf,
        bag_frac=config.bag_fraction,
        max_modes=config.max_nodes,
        seed=config.seed
    )
        
    model.train(
        featues=config.training_data.samples,
        class_label=config.training_data.value,
        predictors=config.predictors
    )
    
    classified = config.stack.classify(model.model)
    
    return RFOutput(
        model=model.model,
        classified=classified,
        samples=config.training_data
    )


class rfmodel:
    def __new__(cls, n_trees: int = 1000, var_per_split: int = None,  min_leaf: int = 1,
                bag_fraction: float = 0.5, max_nodes: int = None, seed: int = 0) -> "ee.Classifier":
        config = {
            "numberOfTrees": n_trees,
            "variablesPerSplit": var_per_split,
            "minLeafPopulation": min_leaf,
            "bagFraction": bag_fraction,
            "maxNodes": max_nodes,
            "seed": seed
        }
        
        return ee.Classifier.smileRandomForest(**config)


def train_rf_model(training_data: ee.FeatureCollection, model: rfmodel, predictors: list = None,
                   class_property: str = None):
    # set defaults
    #TODO validate class_property, make sure it exists after the default value has been set
    
    trained_model = model.train(
        features=training_data,
        classProperty=class_property,
        inputProperties=predictors
    )
    
    return trained_model
        
from __future__ import annotations
from dataclasses import dataclass

import ee

import cfg
import inputs

from eelib import classifiers as rf


@dataclass
class RFOutput:
    model: "ee.Classifier"
    classified: ee.Image
    samples: ee.FeatureCollection


def cnwi_random_forest(config: cfg.RandomForestCFG) -> RFOutput:
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

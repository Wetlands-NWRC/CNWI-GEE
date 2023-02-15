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


class CNWI:
    def __init__(self, config: cfg.RandomForestCFG) -> None:
        self.config = config
    
    def _validate(self):
        # setup the pipeline
        if not isinstance(self.config.stack, inputs._Stack):
            raise TypeError
        
        if self.config.training_data.samples is None:
            self.config.training_data.generate_samples(self.config.stack)
        
        if self.config.predictors:
            condition = all([p in self.config.stack.bandNames().getInfo()
                             for p in self.config.predictors])
            if condition:
                raise Exception("defined predictors not in the current stack")
        
    def run_pipeline(self) -> cfg.RFOutput:
        model = rf.RandomForest(
            n_trees=self.config.n_trees,
            var_per_split=self.config.var_per_split,
            min_leaf_pop=self.config.min_leaf,
            bag_frac=self.config.bag_fraction,
            max_modes=self.config.max_nodes,
            seed=self.config.seed
        )
        
        model.train(
            featues=self.config.training_data.samples,
            class_label=self.config.training_data.value,
            predictors=self.config.predictors
        )
        
        classified = self.config.stack.classify(model.model)
        
        return cfg.RFOutput(
            model=model.model,
            classified=classified,
            samples=self.config.training_data.samples
        )

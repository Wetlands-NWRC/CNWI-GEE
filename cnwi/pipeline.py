from __future__ import annotations

from pipelines import cfg

from eelib import stack
from eelib import classifiers as rf

# Benchmark Pipeline and DataCubePipeline

# Benchmark works off selected image assets from native earth engine collections

# DataCube Pipeline will work off of Image Collections. Sentinel - 1 is a pre selected collection of 
# images and is not dynamically generated

class CNWI:
    def __init__(self, config: cfg.RandomForestCFG) -> None:
        self.config = config
    
    def _validate(self):
        # setup the pipeline
        if not isinstance(self.config.stack, stack._Stack):
            raise TypeError
        
        if self.config.training_data.samples is None:
            self.config.training_data.generate_samples(self.config.stack)
        
        if self.config.predictors:
            condition = all([p in self.config.stack.bandNames().getInfo()
                             for p in self.config.predictors])
            if condition:
                raise Exception("defined predictors not in the current stack")
        
    def run_pipeline(self) -> cfg.RFModel:
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
        
        return cfg.RFModel(
            model=model.model,
            classified=classified,
            samples=self.config.training_data.samples
        )

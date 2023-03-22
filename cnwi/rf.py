from __future__ import annotations

from typing import List
import ee

class RandomForestModel:
        
    def __init__(self, numberOfTrees: int = 1000, variablesPerSplit: int = None,  minLeafPopulation: int = 1,
                bagFraction: float = 0.5, maxNodes: int = None, seed: int = 0) -> None:
        self.numberOfTrees = numberOfTrees
        self.variablesPerSplit = variablesPerSplit
        self.minLeafPopulation = minLeafPopulation
        self.bagFraction = bagFraction
        self.maxNodes = maxNodes
        self.seed = seed
    
    @property
    def classifier(self):
        return ee.Classifer.smileRandomForest(**self.__dict__)

    def train(self, training_data: ee.FeatureCollection, predictors: List[str], classProperty: str) -> "ee.Classifier":
        """trains the random forest model

        Args:
            training_data (ee.FeatureCollection): _description_
            predictors (List[str]): _description_
            classProperty (str): _description_

        Returns:
            ee.Classifier: a tained ee.Classifier Object
        """
        return self.classifier.train(
            features=training_data,
            classProperty=classProperty,
            inputProperties=predictors
        )    

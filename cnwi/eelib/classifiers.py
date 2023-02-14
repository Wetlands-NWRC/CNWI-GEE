from __future__ import annotations

from typing import List, Union

import ee


class RandomForest:
    def __init__(self, n_trees: int, var_per_split: int = None,
                 min_leaf_pop: int = 1, bag_frac: float = 0.5,
                 max_modes: int = None, seed: int = 0) -> None:

        self._cfg = {
            'numberOfTrees': n_trees,
            'variablesPerSplit': var_per_split,
            'minLeafPopulation': min_leaf_pop,
            'bagFraction': bag_frac,
            'maxNodes': max_modes,
            'seed': seed
        }

        self._classifier = ee.Classifier.smileRandomForest(
            **self._cfg
        )

        self._model = None
        self._output_mode = 'CLASSIFICATION'

    @property
    def classifier(self):
        """The classifier property."""
        return self._classifier

    @property
    def model(self):
        """model property, contains the trained model, if the train method
        has not been called will be set to None"""
        return self._model

    @property
    def output_mode(self):
        """The output_mode property."""
        return self._output_mode

    @output_mode.setter
    def output_mode(self, mode: str):
        valid_modes = ['REGRESSION', 'PROBABILITY']
        to_upper = mode.upper()

        if to_upper not in valid_modes:
            raise Exception(f"{to_upper}: is not a valid mode")

        self._output_mode = mode

    def train(self, featues: ee.FeatureCollection, class_label: str,
              predictors: List[str]) -> None:
        self._model = self._classifier.setOutputMode(self._output_mode)\
            .train(**{
                'features': featues,
                'classProperty': class_label,
                'inputProperties': predictors
            })
        return None

    def confusion_matrix(self, labels: ee.List = None) -> Union[ee.ComputedObject, ee.FeatureCollection]:
        """Used to get the confusion matirx from a trained classifier. if the
        labels agrs is specifed will return a feature collection that has a
        features that are formatted to represent how you would view it in
        tabular form. When formatting matrix it will assume that there is a 
        offset of one position. this assuemes that indexing of class values starts
        at 1 not 0. This will assume that the first row of the array is emtpy, and
        will be removed.

        Args:
            labels (ee.List, optional): List of Class Labels. Defaults to None.

        Returns:
            Union[ee.ComputedObject, ee.FeatureCollection]: 
        """
        if self._model is None:
            return None
        cfm = self._model.confusionMatrix()
        if labels is not None:
            cfm = cfm.array().slice(1, 1).slice(0, 1)
            cfml = cfm.toList()

            def format(element) -> ee.Feature:
                clss = labels.get(cfml.indexOf(element))
                col = ee.Dictionary.fromLists([' '], [clss])
                row = ee.Dictionary.fromLists(labels, element)
                props = col.combine(row)
                return ee.Feature(None, props)
            formatted = cfml.map(format)
            return ee.FeatureCollection(formatted)

        else:
            return cfm

from typing import Dict, Any, Callable, List
import ee

from . import imgs

class Sample(ee.FeatureCollection):
    SAMPLE_PROPERTIES = {
        'scale': 10,
        'projection': None,
        'tileScale': 16,
        'properties': ['land_cover', 'value', 'POINT_X', 'POINT_Y'],
        'geometries': False,
    }
    
    @classmethod
    def show_sample_properties(cls) -> Dict[str, Any]:
        return cls.SAMPLE_PROPERTIES
    
    def __init__(self, stack: ee.Image, training_data: ee.FeatureCollection):
        self.stack = stack
        self.training_data = training_data
        super().__init__(self._generate_samples(self.stack, self.training_data))
        
    def _generate_samples(self, stack, training_data):
        return stack.sampleRegions(training_data, **self.SAMPLE_PROPERTIES)


class TrainingData(ee.FeatureCollection):
    
    PROPERTIES = ['land_cover', 'value', 'POINT_X', 'POINT_Y']

    def __init__(self, collection: ee.FeatureCollection, label: str):
        """Constructs a training data table, standardizes inputs.

        NOTE
        ----
        the label argument must be the class labels. Which are the english names. will not work if anything else

        Args:
            collection (ee.FeatureCollection): a feature collection assumed to be a Multipoint collection
            label (str): the column that stores the label information you wish to train on. 
        """
        self.label = label
        self.labels = collection.aggregate_array(self.label).distinct().sort()
        self.values = ee.List.sequence(1, self.labels.size())
        self.lookup = ee.Dictionary.fromLists(self.labels, self.values)
        
        cons = collection.map(self._add_xy).map(self._standardize(self.label, self.lookup)).randomColumn(seed=423)
        super().__init__(cons, None)
    
    # define protected helper functions
    def _standardize(self, column: str, lookup: ee.Dictionary) -> Callable:
        def wrapper(element: ee.Feature):
            key = element.get(column)
            new = element.set({
                'land_cover': ee.String(key).toLowerCase(),
                'value': lookup.get(key) 
            })
            return new.select(self.PROPERTIES)
        return wrapper
    
    def _add_xy(self, element: ee.Feature):
        coords = element.geometry().coordinates()
        x = coords.get(0)
        y = coords.get(1)
        return element.set({'POINT_X': x, 'POINT_Y': y})
    
    
    def generate_samples(self, stack: ee.Image) -> Sample:
        """Sets the sample attribute to the resulting feature collection form sample regions"""
        return Sample(stack, self)


class PartitionData:
    SPLIT = 0.7

    def __init__(self, col: ee.FeatureCollection) -> None:
        self.col = col.randomColumn(seed=435)
        self.training = TrainingData(self.col.filter(f"random < {self.SPLIT}"))
        self.validation = TrainingData(self.col.filter(f"random > {self.SPLIT}"))

    def get_partitioned(self) -> tuple[TrainingData]:
        return self.training, self.validation

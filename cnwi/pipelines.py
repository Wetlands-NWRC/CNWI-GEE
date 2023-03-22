from typing import List, Tuple
import ee

from .eelib import eefuncs
from . import inputs
from . import rf
from . import td


def rf_classification(s1: List[str], s2: List[str], training_data: td.TrainingData, 
                      rectanlge: ee.Geometry, dem: ee.Image = None) -> Tuple[ee.Image, ee.FeatureCollection):
    
    """
    Pipeline will follow this pattern
    take s1, s2, dem inputs do some pre-processing
    
    create stack to sample from
    
    generate samples to train model
    
    create the rf model
    
    train tf model
    
    classify the stack
    
    create an output class, training_samples (with geometry maintained), classified image 
    """
    s1 = inputs.s1_inputs(s1)
    s2 = inputs.s2_inputs(s2)
    
    
    dem = inputs.elevation_inputs(
        rectangle=rectanlge
    )
    
    stack = ee.Image.cat(*s1, *s2, *dem)
    
    td.generate_samples(stack, training_data)
    
    model = rf.RandomForestModel()
    trained = model.train(
        training_data=training_data.samples,
        predictors=stack.bandNames(),
        classProperty=training_data.value
    )
    
    classified_img = stack.classify(trained)
    
    return classified_img, training_data.samples
    
    
    
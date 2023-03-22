from dataclasses import dataclass

import ee

from cnwi import inputs, rf, td, funcs

@dataclass
class EEDataSets:
    s1: list = None
    s2: list = None
    training: dict = None
    region: ee.FeatureCollection = None


def main():
    # load dataset
    dataset = ee.FeatureCollection("<Some Dataset>")
    
    # create a training object
    training = td.TrainingData(
        collection=dataset
    )
    
    # create s1 inputs
    s1s = inputs.s1_inputs(EEDataSets.s1)
    
    # create s2 inputs
    s2s = inputs.s2_inputs(EEDataSets.s2)
    
    # create elevation inputs
    geom = EEDataSets.region.geometry()
    ee_rectangle = funcs.create_rectangle(geom)
    dem = inputs.elevation_inputs(
        rectangle=ee_rectangle
    )
    
    # Create the inputs stack
    stack = ee.Image.cat(*s1s, *s2s, *dem)
    
    # sample the stack
    funcs.generate_samples(
        stack=stack,
        training_data=training
    )
    
    # create the rf model
    model = rf.RandomForestModel()
    # train the model
    trained = model.train(
        training_data=training.samples,
        predictors=stack.bandNames(),
        classProperty=training.value
    )
    
    # classify the image
    classified_img = stack.classify(trained)
    
    # export image and samples to cloud
    return sys.exit(0)
    
    
if __name__ == '__main__':
    main()
import ee

from cnwi import inputs, rf, td, funcs, sfilters
from cnwi import prebuilt


def main():
    # load dataset
    dataset = ee.FeatureCollection("users/ryangilberthamilton/BC/williston/fpca/willistonA_no_floodplain")
    williston = prebuilt.WillistonA()
    
    # create a training object
    training = td.TrainingData(
        collection=dataset,
        label='cDesc'
    )
    
    # create s1 inputs
    s1s = inputs.s1_inputs(williston.s1)
    
    # create s2 inputs
    data_cube_collection = ee.ImageCollection("projects/fpca-336015/assets/williston-cba").filterBounds(dataset)
    s2s = inputs.data_cube_inputs(data_cube_collection)
    
    # create elevation inputs
    elevation = inputs.nasa_dem()
    filter = sfilters.gaussian_filter(3)
    smoothed = filter(elevation)
    slope = ee.Terrain.slope(smoothed)
    
    # Create the inputs stack
    stack = ee.Image.cat(*s1s, *s2s, smoothed, slope)
    
    # sample the stack
    training.sample(
        stack=stack
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
    classified_img = stack.classify(trained).uint8()
    
    # export image and samples to cloud
    return sys.exit(0)
    
    
if __name__ == '__main__':
    main()
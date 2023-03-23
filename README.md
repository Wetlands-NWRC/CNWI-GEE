# CNWI-GEE
Canadian National Wetland Inventory Google Earth Engie Random Forest Classifications. Provides high
level access for doing standardized random forest wetland classifications.

# Installation and Setup
This package is built to be used with the annaconda project. For best user experience use some 
recent version of conda. These walk though will be using a miniconda3
## Dependencies
- Geopandas
- google earth engine

```sh
conda create -n cnwi-gee python=3.10 -c conda-forge earthengine-api geopandas pandas
```

```sh
# Step 2): activate new conda env and authenticate earth engine api
$ conda activate cnwi-gee
# authenticate earth engine api
(cnwi-gee) $ earthengine authenticate
```

# Example Pipeline
```python
from dataclasses import dataclass

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
    s2s = inputs.s2_inputs(williston.s2)
    
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
```

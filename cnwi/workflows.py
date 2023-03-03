import ee

from . import funcs
from . import inputs
from . import rf
from . import td
from .datasets import dem
from .eelib import sf


class _Pipeline:
    def __init__(self, optical, sar, training_data) -> None:
        self.optical = optical
        self.sar = sar
        self.training_data = training_data
        self.dem =  dem.NASADEM_HGT().select('elevation')
        
        self.label_col = 'land_cover' # need to validated the label col

        # TODO will need to add some other paramaters that can be altered before running

    def run(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # consturct TrainingData object
        training_data = td.TrainingData(
            collection = self.training_data,
            label=self.label_col
        )
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # build a rectanlge based off the training data
        listCoords = ee.Array.cat(training_data.collection.geometry().bounds().coordinates(), 1)
        xCoords = listCoords.slice(1, 0, 1)
        yCoords = listCoords.slice(1, 1, 2)

        xMin = xCoords.reduce('min', [0]).get([0,0])
        xMax = xCoords.reduce('max', [0]).get([0,0])
        yMin = yCoords.reduce('min', [0]).get([0,0])
        yMax = yCoords.reduce('max', [0]).get([0,0])

        rectangle = ee.Geometry.Rectangle(xMin, yMin, xMax, yMax)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # build inputs
        optical_inputs = inputs.OpticalInputs(self.optical)
        sar_inputs = inputs.SARInputs(self.sar, sf.Boxcar(1))
        dem_inputs = inputs.DEMInputs(self.dem, rectangle=rectangle)
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # build stack
        image_stack = inputs.stack(
            optical_inputs=optical_inputs,
            sar_inputs=sar_inputs,
            dem_inputs=dem_inputs
        )
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # Generate samples        
        td.generate_samples(
            stack = image_stack,
            training_data = training_data
        )
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # Create Random Forest Config
        rf_config = rf.RandomForestCFG(
            stack = image_stack,
            training_data = training_data
        )
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# 
        # run random forest
        random_forest = rf.cnwi_random_forest(
            config = rf_config
        )
        return random_forest
        

class DataCubeClassification(_Pipeline):
    def __init__(self, optical, sar, training_data) -> None:
        seasons = funcs.data_cube_seasons()
        opt = funcs.parse_season(optical.mean(), seasons)
        if isinstance(sar, ee.ImageCollection):
            sar = funcs.parse_s1_imgs(sar)
        super().__init__(opt, sar, training_data)
        

class EarthEngine:
    pass
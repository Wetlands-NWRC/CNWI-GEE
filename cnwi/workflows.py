from typing import List

import ee

from . import funcs
from . import inputs
from . import rf
from . import td
from .eelib import sf, eefuncs


class _Pipeline:
    def __init__(self, training_data: td.TrainingData, optical: List[ee.Image] = None, sar: List[ee.Image] = None,
                 elevation_dataset: ee.Image = None, region: ee.Geometry = None) -> None:
        self.training_data = training_data
        self.optical = optical
        self.sar = sar
        self.elevation_dataset = elevation_dataset.select('elevation')
        self.region = region

        # pipeline settings
        self.label_col = 'land_cover' # need to validate the label col
        # TODO will need to add some other parameters that can be altered before running

        # validate inputs
        if elevation_dataset is not None and region is None:
            raise Exception("Region needs to spcified")

    def run(self):
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # construct TrainingData object
        training_data = td.TrainingData(
            collection=self.training_data,
            label=self.label_col
        )

        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # build a rectangle based off the training data
        rectangle = eefuncs.create_rectangle(self.region) if self.elevation_dataset is not None else None

        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # build inputs
        optical_inputs = inputs.OpticalInputs(self.optical) if self.optical is not None else None
        sar_inputs = inputs.SARInputs(self.sar, sf.Boxcar(1)) if self.sar is not None else None
        dem_inputs = inputs.DEMInputs(self.elevation_dataset, rectangle=rectangle) \
            if self.elevation_dataset is not None else None
        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # build stack
        image_stack = inputs.stack(
            optical_inputs=optical_inputs,
            sar_inputs=sar_inputs,
            dem_inputs=dem_inputs
        )
        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        # Generate samples        
        td.generate_samples(
            stack=image_stack,
            training_data=training_data
        )
        # #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~# #
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
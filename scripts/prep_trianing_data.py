"""
Idea is to take in training and validation and add some things to it
POINT_X: float
POINT_Y: float
isTraining: int
value: int

write to tmp folder, zip all valid extensions up and move zip to root, remove tmp
"""

import os
import shutil
import sys
import zipfile

from typing import List

import geopandas as gpd
import pandas as pd

FILE_EXTENSIONS = ["shp", "dbf", "prj", "shx", "cpg", "fix", "qix", "sbn", "shp.xml"]


def get_files(dir) -> List[str]:
    filenames = []
    for file in os.listdir(dir):
        _, ext = os.path.splitext(file)
        if ext in FILE_EXTENSIONS:
            filenames.append(os.path.join(dir, file))
    return filenames


def prep_training_data(training, validation, label):
    args = sys.argv
    
    training_filename = args[1]
    validation_filename =args[2]
    label_column_name = args[3]
    
    gdf_t = gpd.read_file(training_filename)
    gdf_v = gpd.read_file(validation_filename)
    
    if 'isTraining' not in gdf_t.columns:
        gdf_t['isTraining'] = 1

    if 'isTraining' not in gdf_v.columns:
        gdf_v['isTraining'] = 0
    
    gdf = pd.concat([gdf_t, gdf_v])
    
    gdf['values'] = gdf[label_column_name]
    land_covers = gdf[land_covers].unique().tolist()
    values = list(range(1, len(land_covers) + 1))
    lookup = dict(zip(land_covers, values))

    gdf.replace({'values': lookup}, inplace=True)
    
    gdf.sort_values(by=[label_column_name], inplace=True)
    gdf.reset_index(inplace=True)
    gdf2 = gdf[[label_column_name, 'value', 'isTraining', 'geometry']]
    gdf = None
    
    if not os.path.exists("./tmp"):
        os.makedirs("./tmp")
    
    gdf2.to_file("./tmp/training_data.shp")
    
    valid_files = get_files("./tmp")
    
    with zipfile.ZipFile("./data.zip", mode='w') as archive:
        for filename in valid_files:
            archive.write(filename)
    
    return None
    

if __name__ == '__main__':
    prep_training_data()

import os
import time

import ee
import geopandas as gpd

from cnwi.fourier import fourier
from cnwi.elev import build_elevation_inpts, NASA_DEM


def load_grid(filename: str) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(filename)
    gdf.to_crs(4326, inplace=True)
    if 'id' not in gdf.columns:
        ids = list(range(1, gdf.shape[0] + 1))
        gdf['id'] = ids
        gdf = gdf[['id', 'geometry']]
        gdf.to_file(filename, driver='GeoJSON')
    return gdf


def cloud_mask(image: ee.Image):
    qa = image.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0)\
        .And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return image.updateMask(mask)


def fourier_transform_2_cloud(grid: gpd.GeoDataFrame, bucket: str, file_prefix: str, filename: str = None) -> None:
    """Does a Fourier Transform on a Sentinel 2 SR Image Collection from 2017 - 2022. The collection 
    has been filtered by cloud pixel percentage (20). It filters the Image Collection by the total
    extent of the defined grid in. It then uses the grid cells to do fine grained filtering on the
    initial image collection before the time series is run through the fourier transformation. 

    FOURIER SETTINGS
    ----------------
    OMEGA = 1
    MODES = 3

    Args:
        grid (gpd.GeoDataFrame): _description_
        bucket (str): _description_
        file_prefix (str): _description_
    """    
    MODES = 3
    DATES = ('2017', '2022')
    
    gdf = grid
    gdf2 = gdf.copy()
    grid_ids = gdf2['id'].unique().tolist()
    grid = ee.FeatureCollection(gdf.__geo_interface__)

    s2_SR = ee.ImageCollection("COPERNICUS/S2_SR").filterBounds(grid)\
        .filterDate(*DATES).filter('CLOUDY_PIXEL_PERCENTAGE < 20').map(cloud_mask)
    print("Exports: Starting")
    for id in grid_ids:
        print(f"Grid ID: {id}")
        # create the intial collection 
        region = grid.filter(f'id == {id}').geometry()
        
        ft = fourier(
            ee_object=s2_SR.filterBounds(region),
            modes=MODES,
            omega=1
        ).clip(region)

        task = ee.batch.Export.image.toCloudStorage(
            image=ft,
            description="",
            bucket=bucket,
            fileNamePrefix=file_prefix + f'/{id}/{filename if filename is not None else "fourier-export"}',
            scale=10,
            crs='EPSG:4326',
            region=region,
            maxPixels=1e13,
            shardSize=256,
            fileDimensions=[4096, 4096],
            skipEmptyTiles=True,
            formatOptions={
                'cloudOptimized': True
            }
        )
        task.start()
    print("Exports: Running on Cloud")
    if not os.path.exists("../logging"):
        os.makedirs("../logging")
    # step into the task monitoring routine
    tasks = ee.batch.Task.list()[:len(grid_ids)]
    ids = [task.id for task in tasks]
    ids.reverse()
    gdf2['FOURIER_TASK_IDS'] = ids
    gdf2.to_file('../logging/fourier-grid.geojson', driver='GeoJSON')
    while any([task.state in ['READY', 'RUNNING'] for task in tasks]):
        time.sleep(10)
        tasks = [task for task in ee.batch.Task.list() if task.id in gdf2['FOURIER_TASK_IDS'].tolist()]

    print("Export: Complete")


def terrain_analysis_2_cloud(grid: gpd.GeoDataFrame, bucket: str, file_prefix: str, filename: str = None):
   
    gdf = grid
    gdf2 = gdf.copy()
    grid_ids = gdf2['id'].unique().tolist()
    grid = ee.FeatureCollection(gdf.__geo_interface__)
    
   
    for grid_id in grid_ids:
        geom = grid.filter(f'id == {grid_id}').geometry()
        dem = NASA_DEM()

        ta = build_elevation_inpts(
            dem=dem,
            aoi=geom
        )

        ta_clp = ta.clip(geom)
        task = ee.batch.Export.image.toCloudStorage(
            image=ta_clp,
            description="",
            bucket=bucket,
            fileNamePrefix=file_prefix + f'/{id}/{filename if filename is not None else "fourier-export"}',
            scale=30,
            fileDimensions=[4096, 4096],
            region=geom,
            crs='EPSG:4326',
            maxPixels=1e13,
            skipEmptyTiles=True,
            formatOptions={
                'cloudOptimized': True
            }
        )
        task.start()
    
    # gets the inital state of the tasks
    print("Exports: Running on Cloud")
    # step into the task monitoring routine
    if not os.path.exists("../logging"):
        os.makedirs("../logging")
    tasks = ee.batch.Task.list()[:len(grid_ids)]
    ids = [task.id for task in tasks]
    ids.reverse()
    gdf2['TERRAIN_TASK_IDS'] = ids
    gdf.to_file('../logging/terrain-grid.geojson', driver='GeoJSON')
    while any([task.state in ['READY', 'RUNNING'] for task in tasks]):
        time.sleep(10)
        tasks = [task for task in ee.batch.Task.list() if task.id in gdf2['TERRAIN_TASK_IDS']\
            .tolist()]
    print("Export: Complete")
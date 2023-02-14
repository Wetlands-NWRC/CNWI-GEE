from typing import List, Union

import ee
import geopandas as gpd


@classmethod
def from_dataframe(cls, dataframe: gpd.GeoDataFrame):
    return cls(dataframe.__geo_interface__)


@classmethod
def from_file(cls, filename, layer: str = None, driver: str = None):
    gdf = gpd.read_file(
        filename=filename,
        driver=driver,
        layer=layer
    ).to_crs(4326)

    return cls(gdf.__geo_interface__)


@classmethod
def from_image_collection(cls, image_collection: ee.ImageCollection):
    raise NotImplementedError


def to_file(self, filename: str, driver: str = None) -> None:
    driver = 'ESRI Shapefile' if driver is None else driver
    gdf = gpd.GeoDataFrame.from_features(self.getInfo().get('features')).\
        set_crs(4326)
    gdf.to_file(filename=filename, driver=driver)
    return None

# Image collection factory class methods


@classmethod
def s1Collection(cls):
    collection_id = 'COPERNICUS/S1_GRD'
    return cls(collection_id)


@classmethod
def s2TOACollection(cls):
    collection_id = "COPERNICUS/S2_HARMONIZED"
    return cls(collection_id)


@classmethod
def s2SRCollection(cls):
    collection_id = "COPERNICUS/S2_SR_HARMONIZED"
    return cls(collection_id)


class Stack(ee.Image):
    def __init__(self, images: List[Union[ee.Image, str]]):
        super().__init__(images)
        self._channel_log = None

    @property
    def channel_log(self) -> ee.FeatureCollection:
        """The channel_log property."""
        bandNames = self.bandNames()
        index = ee.List.sequence(0, bandNames.size().subtract(1))

        zipped = bandNames.zip(index)

        def format(element) -> ee.Feature:
            obj = ee.List(element)
            channel_name = ee.String(obj.get(0))
            index = ee.Number(obj.get(1))
            channel_idx = ee.String('Channel: ').cat(index.add(1).
                                                     format('%02d'))
            return ee.Feature(None, {'00_index': index,
                                     '01_Channel_index': channel_idx,
                                     '02_Channel_name': channel_name})

        features = zipped.map(format)
        return ee.FeatureCollection(features)

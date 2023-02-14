from typing import List

import ee

from . import plcfgs


class eeLogger(ee.FeatureCollection):
    def __init__(self, args, opt_column=None):
        super().__init__(args, opt_column)

    @classmethod
    def Sentinel1_Logger(cls, images: List[ee.Image]):
        """ extracts date and system id. images are for images that natively 
        exists with in earth engines data catalogue."""
        PLATFORM = 'Sentinel - 1'

        def fmt(element: ee.Image) -> ee.Feature:
            sysidx = element.get('system:index')
            date = element.date().format('YYYY-MM-dd')
            props = {'date': date, 'platform': PLATFORM,
                     'sys_idx': sysidx}
            return ee.Feature(None, props)

        return cls([fmt(_) for _ in images])

    @classmethod
    def S1LSCLogger(cls, collection: ee.ImageCollection):
        PLATFORM = 'Sentinel - 1'

        def fmt(element) -> ee.Feature:
            element = ee.Image(element)
            sysidx = element.get('system:index')
            date = element.date().format('YYYY-MM-dd')
            props = {'date': date, 'platform': PLATFORM,
                     'sys_idx': sysidx}
            return ee.Feature(None, props)

        asList = collection.toList(collection.size())
        featureList = asList.map(fmt)
        return cls(featureList)

    @classmethod
    def Sentinel2_logger(cls, images: List[ee.Image]):
        """ extracts date and system id. images are for images that natively 
        exists with in earth engines data catalogue."""
        PLATFORM = 'Sentinel - 2'

        def fmt(element: ee.Image) -> ee.Feature:
            sysidx = element.get('system:index')
            date = element.date().format('YYYY-MM-dd')
            props = {'date': date, 'platform': PLATFORM,
                     'sys_idx': sysidx}
            return ee.Feature(None, props)

        return cls([fmt(_) for _ in images])

    @classmethod
    def lookup(cls, collection: ee.FeatureCollection, label_col: str,
               value_col: str, colors: ee.Dictionary):

        labels = collection.aggregate_array(label_col).distinct()
        values = collection.aggregate_array(value_col).distinct()
        zipped = labels.zip(values)

        def fmt(element: ee.List):
            eelist = ee.List(element)
            label = eelist.get(0)
            value = eelist.get(1)
            count = collection.filter(ee.Filter.eq(label_col, label)).size()
            props = {'00_label': label, '01_value': value,
                     '02_count': count, '03_hex': colors.get(label)}
            return ee.Feature(None, props)

        return cls(zipped.map(fmt))

    @classmethod
    def predictors(cls, predictors: ee.List):

        def func(element):
            return ee.Feature(None, {'predictor': element})

        return cls(predictors.map(func))


class DatacubeLogger(ee.ImageCollection):

    def __init__(self, args):
        super().__init__(args)

    def tile_IDs(self) -> ee.FeatureCollection:
        """Data Cube Tile Logger"""
        tile_ids = self.aggregate_array('tileID')
        system_index = self.aggregate_array('system:index')

        zipped = tile_ids.zip(system_index)

        def fmt(element: ee.List) -> ee.Feature:
            eelist = ee.List(element)
            tileid = eelist.get(0)
            sysidx = eelist.get(1)
            return ee.Feature(None, {"tileID": tileid, "sys_index": sysidx})

        return ee.FeatureCollection(zipped.map(fmt))

    def datacube_dates(self) -> ee.FeatureCollection:
        cfg = plcfgs.DataCubeCfg()
        seasons = cfg.seasons
        dates = [{'00_Season': key, '01_start': value.get('start'),
                  '02_end': value.get('end')}
                 for key, value in seasons.items()]
        features = [ee.Feature(None, item) for item in dates]
        return ee.FeatureCollection(features)

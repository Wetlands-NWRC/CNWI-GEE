import os

from itertools import combinations
from typing import Dict, Any, Union, List

import ee
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import eefuncs


def eemoa(image: ee.Image, label_col: str, pts: ee.FeatureCollection) -> ee.FeatureCollection:

    def moaFeatures(list: ee.List, c1, c2):
        list = ee.List(list)
        vs_classes = f'{c1}:{c2}'

        def moaFeature(element):
            nest = ee.List(element)
            band = nest.get(0)
            value = nest.get(1)
            return ee.Feature(None, {'00_Classes': vs_classes,
                                     '02_Band': band, '03_Value': value})
        return list.map(moaFeature)

    def moaRanks(fc) -> ee.Dictionary:
        bands = fc.aggregate_array('02_Band')
        ranks = ee.List.sequence(1, bands.size())
        return ee.Dictionary.fromLists(bands, ranks)

    def instertRanks(fc, ranksLookup):
        def inner_func(element):
            band = element.get('02_Band')
            rank = ranksLookup.get(band)
            return element.set('01_Rank', rank)
        return fc.map(inner_func)

    samples = image.sampleRegions(**{
        'collection': pts,
        'tileScale': 16,
        'scale': 10,
        'properties': [label_col]
    })

    labels = pts.aggregate_array(label_col).distinct().getInfo()
    predicts = image.bandNames()
    combs = combinations(labels, 2)

    collections = []
    for comb in combs:
        c1, c2 = comb
        moa_values = eefuncs.moa_calc(
            samples=samples,
            predictors=predicts,
            label_col=label_col,
            c1=c1,
            c2=c2
        )
        features = moaFeatures(moa_values, c1, c2)
        moaFc = ee.FeatureCollection(features)
        moaSort = moaFc.sort("03_Value", False)
        rankLkup = moaRanks(moaSort)
        moaRanked = instertRanks(moaSort, rankLkup)
        collections.append(moaRanked)
    return ee.FeatureCollection(collections).flatten()



    # Step 3: select the collection based on do lazy loading


class MoaTable(pd.DataFrame):
    def __init__(self, dfin: pd.DataFrame, label: str) -> None:
        labels = dfin[label].unique().tolist()
        # set combinations
        label_combs = combinations(labels, 2)
        
        # group dataframe by land cover
        land_covers = {land_cover: dfin[(dfin[label] == land_cover)] for land_cover in labels}
        
        column = [i for i in dfin.columns if i not in ['.geo', 'system:index', 'CID', label,
                                                       'land_value', 'id', 'geometry']]
        
        dfs = []
        for comb in label_combs:
            ref = land_covers.get(comb[0])
            trg = land_covers.get(comb[1])
            
            scores = []
            for land_cover in column:
                a1 = ref[land_cover].to_numpy()
                a2 = trg[land_cover].to_numpy()
                
                a1m = a1.mean()
                a2m = a2.mean()
                
                cat = np.concatenate((a1, a2))
                
                total_std = cat.std()
                
                value = abs((a2m - a1m) / total_std)
                scores.append(value)

            array = np.array(scores)
            dfmoa = pd.DataFrame(data={'band': column, 'scores': array})
            df_sort = dfmoa.sort_values(by='scores', ascending=False)
            df_sort['rank'] = np.arange(1, len(column) + 1)
            df_sort['labels'] = [f'{comb[0]}:{comb[1]}' for _ in range(0, len(column))]
            dfs.append(df_sort)
        moa_table = pd.concat(dfs, axis=0, ignore_index=True)
        moa_table = moa_table[['labels', 'rank', 'band', 'scores']]
        super().__init__(moa_table)
        self._samples = dfin

    def plot_moa_dis(self, predictors: List[Any], dir: str = None) -> None:
        
        dir = './plotting' if dir is None else dir
        
        def hist_factory(series: pd.Series, title: str, bin: Union[str, int] = None):
            bin = 'auto' if bin is None else bin
            
            n, bins, patches = plt.hist(series, bin, rwidth=0.85)

            plt.xlabel('Value')
            plt.ylabel('Frequency')
            plt.title(title)

            maxfreq = n.max()
            plt.ylim(ymax=np.ceil(maxfreq / 100) * 100 if maxfreq % 100 
                    else maxfreq + 100)
            
            plt.grid(True)
            return n, bins, patches

        for band in predictors:
            series = self._samples[band]
            
            hist_factory(
                series=series,
                title=band,
                bin=100
            )
            if not os.path.exists(dir):
                os.makedirs(dir)

            plotname = os.path.join(dir, f'{band}.png')
            
            plt.savefig(plotname)
            plt.close()
        return None

    def extract_by_rank(self, rank: int = 1) -> List[Any]:
        df = self[self['rank'] == rank]
        bands = df['band'].unique().tolist()
        return bands
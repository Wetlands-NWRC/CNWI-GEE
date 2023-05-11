from itertools import combinations

import pandas as pd
import numpy as np


class MOATable(pd.DataFrame):
    def __init__(self, table) -> None:
        super().__init__(table)


def moa_calc(dfin: pd.DataFrame, label: str) -> MOATable:
    labels = dfin[label].unique().tolist()
    # set combinations
    label_combs = combinations(labels, 2)
    
    # group dataframe by land cover
    land_covers = {land_cover: dfin[(dfin[label] == land_cover)] for land_cover in labels}
    
    column = [i for i in dfin.columns if i not in ['.geo', 'system:index', 'CID', label,
                                                    'land_value', 'id', 'geometry', 'POINT_X',
                                                    'POINT_Y', 'isTraining', 'value', 'index']]
    
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
    return MOATable(moa_table)
from __future__ import annotations

import enum

import pandas as pd

class LandValues(enum.Enum):
    BOG = 1
    FEN = 2
    FOREST = 3
    MARSH = 4
    SHALLOW_WATER = 5
    SWAMP = 6
    UPLAND = 7
    WATER = 8    


class LandColours(enum.Enum):
    BOG = 'A52A2A'
    FEN = 'FFF600'
    FOREST = 'FF0000'
    MARSH = '8FBC8F'
    SHALLOW_WATER = '7CFC00'
    SWAMP = '008000'
    UPLAND = 'FF0001'
    WATER = '0000FF'


class LandCovers:
    def __init__(self, labels: list[str]) -> None:
        self.labels = labels

        keys = [str(_.name).upper() for _ in LandValues]
        self.labels = [_.upper() for _ in self.labels]
        
        if any([key in self.labels for key in keys]) == False:
            raise Exception("Label is not in LandValues")

    @property
    def colours(self) -> dict[str, str]:
        c = {str(obj.name): str(obj.value) for obj in LandColours
                if str(obj.name) in self.labels}
        c = dict(sorted(c.items(), key=lambda item: item[0]))
        return c 

    @property
    def palette(self) -> list[str]:
        pallette = [
            f'#{self.colours.get(label)}' for label in self.labels
        ]
        return pallette


class CMAP(pd.DataFrame):
        
    def __init__(self, land_cover: LandCovers) -> None:
        
        labels, value, r, g, b = [], [], [], [], []
        
        for idx, item in enumerate(land_cover.colours.items(), start=1):
            label, hex = item
            rgb: tuple[int] = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            r.append(rgb[0]); g.append(rgb[1]); b.append(rgb[2]); value.append(idx), labels.append(label)
        
        data={"value": value, "red": r, "green": g, "blue": b}
        super().__init__(pd.DataFrame(data=data, index=labels))
    
    def to_clr(self, filename: str):
        self.to_csv(
            path_or_buf=filename,
            sep=" ",
            header=False,
            index=False
        )
        

class AAFC(enum.Enum):
    pass
        
        
        
    
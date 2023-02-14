from __future__ import annotations

import enum

import pandas as pd

class LandValues(enum.Enum):
    Bog = 1
    Fen = 2
    Forest = 3
    Marsh = 4
    Shallow_Water = 5
    Swamp = 6
    Upland = 7
    Water = 8    


class LandColours(enum.Enum):
    Bog = 'A52A2A'
    Fen = 'FFF600'
    Forest = 'FF0000'
    Marsh = '8FBC8F'
    Shallow_Water = '7CFC00'
    Swamp = '008000'
    Upland = 'FF0001'
    Water = '0000FF'


class LandCovers:
    def __init__(self, labels: list[str]) -> None:
        self.labels = labels

        keys = [str(_).lower() for _ in LandValues()]
        self.labels = [_.lower() for _ in self.labels]
        
        if any([key in self.labels for key in keys]) == False:
            raise Exception("Label is not in LandValues")

    @property
    def colours(self) -> dict[str, str]:
        c = {str(obj.name): str(obj.value) for obj in LandColours
                if str(obj.name) in self.labels}
        return dict(sorted(c.items(), key=lambda item: item[1])) 

    @property
    def palette(self) -> list[str]:
        pallette = [
            f'#{self.colours.get(label)}' for label in self.labels
        ]
        return pallette


class CMAP(pd.DataFrame):
        
    def __init__(self, land_cover: LandCovers) -> None:
        
        value, r, g, b = [], [], [], []
        
        for idx, hex in enumerate(land_cover.colours.values(), start=1):
            rgb: tuple[int] = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            r.append(rgb[0]); g.append(rgb[1]); b.append(rgb[2]); value.append(idx)
        
        data={"value": value, "red": r, "green": g, "blue": b}
        super().__init__(pd.DataFrame(data=data))
    
    def to_clr(self, filename: str):
        self.to_csv(
            path_or_buf=filename,
            sep=" ",
            header=False,
            index=False
        )
        
                
        
        
        
    
from __future__ import annotations

import enum
from typing import Type
import pandas as pd


class ColorPalette(enum.Enum):
    """
    Base class for creating a Color Palette the key is assumed to be the land cover class
    and the value is assumed to be the hex code that represents the disired color of the land cover
    classes
    
    Example 
    -------
    ```
    class SubLandCovers(_LandCovers):
        BOG = 'A52A2A'
        FEN = 'FFF600'
        FOREST = 'FF0000'
        MARSH = '8FBC8F'
        SHALLOW_WATER = '7CFC00'
        SWAMP = '008000'
        UPLAND = 'FF0001'
        WATER = '0000FF'
    ```
    """
    pass

    @classmethod
    def color_pallet(cls):
        return [f'#{_.name}' for _ in cls]


class CMAP(pd.DataFrame):
    # TODO fix this tool
    def __init__(self, color_pallet: ColorPalette) -> None:
        self.color_pallet = color_pallet
        labels, value, r, g, b = [], [], [], [], []
        inputs = zip(self._get_labels, self._get_hex)
        for idx, pkg in enumerate(inputs, start=1):
            label, hex_c = None, None 
            rgb: tuple[int] = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
            r.append(rgb[0])
            g.append(rgb[1])
            b.append(rgb[2])
            value.append(idx), labels.append(label)

        data = {"value": value, "red": r, "green": g, "blue": b}
        super().__init__(pd.DataFrame(data=data, index=labels))

    def _get_labels(self):
        return [str(_.name) for _ in self.color_pallet]
    
    def _get_hex(self):
        return [_.value for _ in self.color_pallet]
    

    def to_clr(self, filename: str):
        self.to_csv(
            path_or_buf=filename,
            sep=" ",
            header=False,
            index=False
        )

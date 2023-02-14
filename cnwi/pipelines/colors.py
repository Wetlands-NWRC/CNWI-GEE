from enum import Enum
from typing import List

import ee


class Colors(Enum): 
    """ Hex color codes for each land cover class """
    Ag = "F5DEB3"
    Bog = 'A52A2A'
    Fen = 'FFF600'
    Forest = 'FF0000'
    Marsh = '8FBC8F'
    SH_Water = '7CFC00'
    Swamp = '008000'
    Upland = 'FF0001'
    Water = '0000FF'

    @classmethod
    def to_eeDict(cls) -> ee.Dictionary:
        return ee.Dictionary({str(color.name): color.value for color in cls})

    @classmethod
    def mkcmap(cls, filename: str, labels: List[str] = None) -> None:
        
        landcovers = {str(_.name): _.value for _ in cls}
        
        def hex2rgb(h):
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

        cmap = []
        for idx, label in enumerate(labels, start=1):
            color = landcovers.get(label, 'None')
            
            if color is None:
                raise ValueError(f"{label} not in Colors ...")
            
            rgb_values = hex2rgb(color)
            rgb = '{} {} {} {}\n'.format(idx, *rgb_values)
            cmap.append(rgb)

        with open(filename, 'w') as colormap:
            colormap.writelines(cmap)
        
        return None


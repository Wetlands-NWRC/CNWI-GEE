from __future__ import annotations

import enum


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
        return {str(obj.name): str(obj.value) for obj in LandColours
                if str(obj.name) in self.labels}

    @property
    def palette(self) -> list[str]:
        pallette = [
            f'#{self.colours.get(label)}' for label in self.labels
        ]
        return pallette
    
import enum


class LandColours(enum.Enum):
    Bog = None
    Fen = None
    Forest = None
    Marsh = None
    Shallow_Water = None
    Swamp = None
    Upland = None
    Water = None


class LandValues(enum.Enum):
    Bog = 1
    Fen = 2
    Forest = 3
    Marsh = 4
    Shallow_Water = 5
    Swamp = 6
    Upland = 7
    Water = 8    
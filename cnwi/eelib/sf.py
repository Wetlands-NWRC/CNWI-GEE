from abc import ABC

import ee


class SpatialFilter(ABC):
    pass


class Boxcar(SpatialFilter):

    def __new__(cls, radius: float, units: str = None, normalize: bool = True,
                magnitude: float = 1.0):
        """Used to construct a new ee.Kernel.square object. This is also
        what is used to represent a box car filter

        Args:
            radius (float): _description_
            units (str, optional): _description_. Defaults to pixels.
            normalize (bool, optional): _description_. Defaults to True.
            magnitude (float, optional): _description_. Defaults to 1.0.
        """

        units = 'pixels' if units is None else units

        return ee.Kernel.square(radius, units, normalize, magnitude)

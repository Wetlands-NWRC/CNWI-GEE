from typing import Callable

import ee
from .datasets import dem


def slope_mask(slope: ee.Image, deg: int = 15) -> Callable:
    """Creates a masked image from a slope input

    Args:
        slope (ee.Image): a single banded image that represents the slope
        deg (int, optional): Degree threshold. Defaults to 15.

    Returns:
        Callable: a function that can be used to mask out slope
    """    """"""
    def slope_mask_wrapper(image: ee.Image) -> ee.Image:
        mask = slope.lt(deg)
        return image.updateMask(mask)
    return slope_mask_wrapper
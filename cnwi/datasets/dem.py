from typing import Callable

import ee


class CDEM:
    def __new__(cls, viewport: ee.Geometry = None, kernel=None, size: int = 1, resample_m: str = 'bicubic') -> ee.Image:
        def resample(element): return element.resample(resample_m)

        def apply_filter(filter, size) -> Callable:
            spf = filter(size)

            def apply_filter_wrapper(element: ee.Image) -> ee.Image:
                return element.convolve(spf)

            return apply_filter_wrapper

        instance = ee.ImageCollection("NRCan/CDEM")

        if viewport is not None:
            instance = instance.filterBounds(viewport)

        instance = instance.map(resample)

        if kernel is not None:
            instance = instance.map(apply_filter(kernel, size))

        return instance

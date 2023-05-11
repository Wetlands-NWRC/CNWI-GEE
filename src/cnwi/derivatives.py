from abc import ABC, abstractmethod
from typing import Any, List

import ee


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
class _RasterCalculator:
    NAME = None
    
    def __call__(self, image: ee.Image) -> Any:
        results = self._calculation(image)
        return image.addBands(results)
    
    def _calculation(self, image: ee.Image):
        pass
    
    def calculate(self, image: ee.Image):
        return image.addBands(self._calculation(image))


class NDVI(_RasterCalculator):
    
    NAME = 'NDVI'
    
    def __init__(self, nir: str = None, red: str = None) -> None:
        super().__init__()
        self.nir = 'B8' if nir is None else nir
        self.red = 'B4' if red is None else red
 
    def _calculation(self, image) -> ee.Image:
        return image.normalizedDifference([self.nir, self.red]).rename(self.NAME)


class SAVI(_RasterCalculator):
    
    NAME = 'SAVI'
    
    def __init__(self, nir: str = None, red: str = None, coef: float = 0.5) -> None:
        super().__init__()
        self.nir = 'B8' if nir is None else nir
        self.red = 'B4' if red is None else red
        self.coef = coef
    
    def _calculation(self, image: ee.Image):
        # select bands
        nir_band = image.select(self.nir)
        red_band = image.select(self.red)
        ee_coef = ee.Number(self.coef)

        exp = '((NIR - RED) / (NIR + RED)) * (1 + COEF)'
        opt_map = {'NIR': nir_band, 'RED': red_band, 'COEF': ee_coef}

        savi = image.expression(
            expression=exp,
            opt_map=opt_map
        )

        return savi.rename(self.NAME)


class TasselCap(_RasterCalculator):
    
    NAME = ['Brightness', 'Greenness', 'Wetness']
    
    def __init__(self, blue: str = None, red: str = None, green: str = None, nir: str = None, 
                 swir_1: str = None, swir_2: str = None) -> None:
        super().__init__()
        self.blue = 'B2' if blue is None else blue
        self.red = 'B4' if red is None else red
        self.green = 'B3' if green is None else green
        self.nir = 'B8' if nir is None else nir
        self.swir_1 = 'B11'if swir_1 is None else swir_1
        self.swir_2 = 'B12'if swir_2 is None else swir_2

    def _calculation(self, image: ee.Image):
        image = image.select([
            self.blue, 
            self.red,
            self.green,
            self.nir,
            self.swir_1,
            self.swir_2
        ])

        co_array = [
            [0.3037,   0.2793,  0.4743,  0.5585,  0.5082,  0.1863],
            [-0.2848, -0.2435, -0.5436,  0.7243,  0.0840, -0.1800],
            [0.1509,   0.1973,  0.3279,  0.3406, -0.7112, -0.4572]
        ]

        co = ee.Array(co_array)

        arrayImage1D = image.toArray()
        arrayImage2D = arrayImage1D.toArray(1)

        components_image = ee.Image(co). \
            matrixMultiply(arrayImage2D). \
            arrayProject([0]). \
            arrayFlatten([self.NAME])

        return components_image        


class Ratio(_RasterCalculator):
    def __init__(self, numerator: str, denominator: str) -> None:
        super().__init__()
        self.numer = numerator
        self.denom = denominator
    
    def _calculation(self, image: ee.Image):
        exp = "x / y"
        opt_map = {
            'x': image.select(self.numer),
            'y': image.select(self.denom)
        }

        derv = image.expression(
            expression=exp,
            opt_map=opt_map
        )   
        return derv.rename(f'Ratio_{self.numer}_{self.denom}')

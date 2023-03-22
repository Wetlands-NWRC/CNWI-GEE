from typing import List

import ee
import tagee


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Optical Derivatives
def ndvi(image: ee.Image, nir: str = None, red: str = None):
    nir = 'B8' if nir is None else nir
    red = 'B4' if red is None else red

    return image.normalizedDifference([nir, red]).rename('NDVI')


def savi(image: ee.Image, nir: str = None, red: str = None, coef: float = 0.5):
    nir = 'B8' if nir is None else nir
    red = 'B4' if red is None else red

    # select bands
    nir_band = image.select(nir)
    red_band = image.select(red)
    ee_coef = ee.Number(coef)

    exp = '((NIR - RED) / (NIR + RED)) * (1 + COEF)'
    opt_map = {'NIR': nir_band, 'RED': red_band, 'COEF': ee_coef}

    savi = image.expression(
        expression=exp,
        opt_map=opt_map
    )

    return savi.rename('SAVI')


def tassel_cap(mage: ee.Image, blue: str = None, red: str = None,
                green: str = None, nir: str = None, swir_1: str = None,
                swir_2: str = None) -> ee.Image:

    # set defult band mappings
    blue = 'B2' if blue is None else blue
    red = 'B4' if red is None else red
    green = 'B3' if green is None else green
    nir = 'B8' if nir is None else nir
    swir_1 = 'B11'if swir_1 is None else swir_1
    swir_2 = 'B12'if swir_2 is None else swir_2

    image = image.select([
        blue, red, green, nir, swir_1, swir_2
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
        arrayFlatten([['Brightness', 'Greenness', 'Wetness']])

    return components_image


def batch_create_ndvi(images: List[ee.Image], nir: str = None, red: str = None) -> List[ee.Image]:
    return [ndvi(img, NIR=nir, RED=red) for img in images]


def batch_create_savi(images: List[ee.Image], nir: str = None, red: str = None,
                      coef: float = 0.5) -> List[ee.Image]:
    return [savi(image=img, NIR=nir, RED=red, coef=coef) for img in images]


def batch_create_tassel_cap(images: List[ee.Image], blue: str = None, red: str = None,
                            green: str = None, nir: str = None, swir_1: str = None,
                            swir_2=None) -> List[ee.Image]:
    return [tassel_cap(image=img, blue=blue, red=red, green=green,
                             nir=nir, swir_1=swir_1, swir_2=swir_2)
             for img in images]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# RaDAR Derivatives
def ratio(image, numerator: str, denominator: str) -> ee.Image:
    exp = "x / y"
    opt_map = {
        'x': image.select(numerator),
        'y': image.select(denominator)
    }

    derv = image.expression(
        expression=exp,
        opt_map=opt_map
    )

    return derv.rename('Ratio')


def batch_create_ratio(images: List[ee.Image], numerator: str, denominator: str) -> List[ee.Image]:
    return [ratio(img, numerator, denominator) for img in images]
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# DEM Derivatives
def terrain_analysis(dem: ee.Image, bbox: ee.Geometry) -> ee.Image:
    # TODO get actual band names
    bands = ['Elevation', 'Slope', 'Horizontal curvature', 'Vertical curvature', 'Mean curvature', 'Gaussian curvature']
    return tagee.terrainAnalysis(dem, bbox).select(bands)


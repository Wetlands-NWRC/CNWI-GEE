import ee


# Optical Derivatives
class NDVI:

    def __new__(cls, image: ee.Image, NIR: str = None, RED: str = None):
        """Band Mappings default to Sentinel - 2. Used to construct a new
        ee.Image that represents a NDVI ouput.

        Args:
            image (ee.Image): _description_
            NIR (str, optional): the NIR Band. Defaults to B8.
            RED (str, optional): The Red band. Defaults to B4.
        """
        NIR = 'B8' if NIR is None else NIR
        RED = 'B4' if RED is None else NIR

        return image.normalizedDifference([NIR, RED]).rename('NDVI')


class SAVI:

    def __new__(cls, image: ee.Image, NIR: str = None, RED: str = None,
                coef: float = 0.5) -> ee.Image:
        """Band Mappings default to Sentinel - 2. Used to construct a new
        ee.Image that represents a SAVI ouput.

        Args:
            image (ee.Image): _description_
            NIR (str, optional): the NIR Band. Defaults to B8.
            RED (str, optional): The Red band. Defaults to B4.
        """
        NIR = 'B8' if NIR is None else NIR
        RED = 'B4' if RED is None else NIR

        # select bands
        nir_band = image.select(NIR)
        red_band = image.select(RED)
        ee_coef = ee.Number(coef)

        exp = '((NIR - RED) / (NIR + RED)) * (1 + COEF)'
        opt_map = {'NIR': nir_band, 'RED': red_band, 'COEF': ee_coef}

        savi = image.expression(
            expression=exp,
            opt_map=opt_map
        )

        return savi.rename('SAVI')


class TasselCap:
    def __new__(cls, image: ee.Image, blue: str = None, red: str = None,
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


# SAR Derivatives
class Ratio:

    def __new__(cls, image: ee.Image, numerator: str, denominator: str):

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


# DEM Derivatives
class Slope:

    def __new__(cls, image: ee.Image, elevation: str) -> ee.Image:
        return ee.Terrain.slope(image.select('elevation'))

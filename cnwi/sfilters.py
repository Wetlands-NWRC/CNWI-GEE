from typing import Callable

import ee


def boxcar(radius: float, units: str = None, normalize: bool = True, magnitude: float = 1.0) -> Callable:
    units = 'pixels' if units is None else units
    s_filter = ee.Kernel.square(radius, units, normalize, magnitude)
    def wrapper(image: ee.Image):
        return image.convolve(s_filter)
    return wrapper

def gaussian_filter(radius: float, sigma: int = 1, units: str = None, normalize: bool = True, magnitude: float = 1.0) -> Callable:
    units = 'pixels' if units is None else units
    s_filter = ee.Kernel.gaussian(radius=radius, sigma=sigma, units=units, normalize=normalize, magnitude=magnitude)
    def wrapper(image: ee.Image):
        return image.convolve(s_filter)
    return wrapper


def perona_malik(K=3.5, iterations=10, method=2) -> Callable:
    """translated from this example here https://mygeoblog.com/2021/01/22/perona-malik-filter/

    Args:
        k (float, optional): _description_. Defaults to 3.5.
        iter (int, optional): _description_. Defaults to 10.
        method (int, optional): _description_. Defaults to 2.

    Returns:
        callable: _description_
    """
    def wrapper(img: ee.Image):
        dxW = ee.Kernel.fixed(3, 3,
                            [[ 0,  0,  0],
                            [ 1, -1,  0],
                            [ 0,  0,  0]]);

        dxE = ee.Kernel.fixed(3, 3,
                                [[ 0,  0,  0],
                                    [ 0, -1,  1],
                                    [ 0,  0,  0]]);
        
        dyN = ee.Kernel.fixed(3, 3,
                                [[ 0,  1,  0],
                                    [ 0, -1,  0],
                                    [ 0,  0,  0]]);
        
        dyS = ee.Kernel.fixed(3, 3,
                                [[ 0,  0,  0],
                                    [ 0, -1,  0],
                                    [ 0,  1,  0]]);

        lamb = 0.2;

        k1 = ee.Image(-1.0/K);
        k2 = ee.Image(K).multiply(ee.Image(K));

        for _ in range(0, iterations): 
            dI_W = img.convolve(dxW)
            dI_E = img.convolve(dxE)
            dI_N = img.convolve(dyN)
            dI_S = img.convolve(dyS)

            match method:
                case 1:
                    cW = dI_W.multiply(dI_W).multiply(k1).exp();
                    cE = dI_E.multiply(dI_E).multiply(k1).exp();
                    cN = dI_N.multiply(dI_N).multiply(k1).exp();
                    cS = dI_S.multiply(dI_S).multiply(k1).exp();
                
                    img = img.add(ee.Image(lamb).multiply(cN.multiply(dI_N).add(cS.multiply(dI_S))\
                        .add(cE.multiply(dI_E)).add(cW.multiply(dI_W))))

                case 2:
                    cW = ee.Image(1.0).divide(ee.Image(1.0).add(dI_W.multiply(dI_W).divide(k2)));
                    cE = ee.Image(1.0).divide(ee.Image(1.0).add(dI_E.multiply(dI_E).divide(k2)));
                    cN = ee.Image(1.0).divide(ee.Image(1.0).add(dI_N.multiply(dI_N).divide(k2)));
                    cS = ee.Image(1.0).divide(ee.Image(1.0).add(dI_S.multiply(dI_S).divide(k2)));
                
                    img = img.add(ee.Image(lamb).multiply(cN.multiply(dI_N).add(cS.multiply(dI_S))\
                        .add(cE.multiply(dI_E)).add(cW.multiply(dI_W))))

        return img
    return wrapper
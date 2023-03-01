from abc import ABC

import ee

# TODO implement boxcar function that follow the same pattern as peroan malik 
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


def perona_malik(k:float = 3.5, iter: int = 10, method: int = 2) -> callable:
    """translated from this example here https://mygeoblog.com/2021/01/22/perona-malik-filter/

    Args:
        k (float, optional): _description_. Defaults to 3.5.
        iter (int, optional): _description_. Defaults to 10.
        method (int, optional): _description_. Defaults to 2.

    Returns:
        callable: _description_
    """    
    def perona_malik_wrapper(image: ee.Image):
        K = k
        iter = iter
        method = method
        
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

        for _ in range(0, iter): 
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
    return perona_malik_wrapper
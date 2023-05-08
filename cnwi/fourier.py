import math
from typing import List, Callable, Tuple
import ee

from . import derivatives as d


class model:    
    def __init__(self, ee_object: ee.ImageCollection, modes: int = 5, dependent_var: str = None) -> None:
        self.modes = list(range(1, modes + 1))
        self.cos_names = [f'cos_{ _ }' for _ in self.modes]
        self.sin_name = [f'sin_{ _ }' for _ in self.modes]
        self.independent = ['constant', 't', *self.sin_name, *self.cos_names]
        self.dependent = dependent_var
        self.harmonics = ee_object.map(self._add_harmonics(
            freq=self.modes,
            cos_names=self.cos_names,
            sin_names=self.sin_name
        ))
        
        self.trend = self.harmonics.select([*self.independent, dependent_var]).\
            reduce(ee.Reducer.linearRegression(**{
                'numX': len(self.independent),
                'numY': 1
            }))
        
        self.coefficients: ee.Image = self.trend.select('coefficients').\
            arrayFlatten([self.independent, ["coeff"]])

        ee_object = None
    
    def _add_harmonics(freq: List[int], cos_names: List[str], sin_names: List[str]) -> Callable:    
        def add_harmonics_wrapper(element: ee.Image):
            frequencies = ee.Image.constant(freq)
            time = ee.Image(element).select('t')
            cosines = time.multiply(frequencies).cos().rename(cos_names)
            sines = time.multiply(frequencies).sin().rename(sin_names)
            return element.addBands(cosines).addBands(sines)
        return add_harmonics_wrapper


class Phase(ee.Image):
    
    def __init__(self, coeff: ee.Image, mode: int):
        super().__init__(self._calc(coeff, mode))
    
    def _calc(self, coeff, mode) -> ee.Image:
        sin, cos, name = f'sin_{mode}_coeff', f'cos_{mode}_coeff', f'phase_{mode}'
        return coeff.select(sin).atan2(coeff.select(cos)).rename(name)
         

class Amplitude(ee.Image):
    def __init__(self, coeff: ee.Image, mode: int):
        super().__init__(self._calc(coeff, mode), None)

    def _calc(self, coeff, mode) -> ee.Image:
        sin, cos, name = f'sin_{mode}_coeff', f'cos_{mode}_coeff', f'amp_{mode}'
        return coeff.select(sin).atan2(coeff.select(cos)).rename(name)
         

class FourierImage(ee.Image):
    
    def __init__(self, transformation: ee.ImageCollection):
       
        # reduce to median
        stack = transformation.median().unitScale(-1, 1)
        coeff_bands = stack.select(".*coeff")
        amp_bands = stack.select('amp.*')
        phase_bands = stack.select('phase.*')

        super().__init__(ee.Image.cat(coeff_bands, amp_bands, phase_bands), None)


class FourierTransform:
    def __init__(self, model: model, col: ee.ImageCollection) -> None:        
        # select coeff
        coeff = model.coefficients.select('.*coeff')
        # add coeff to each band in the collection
        self.w_coeff = col.map(lambda x: x.addBands(coeff))
        
        self.fit = self._add_amps_phases(
            model=model,
            input_col=col
        )
    
    def _add_phase(self, coeff, mode) -> Callable:
        def wrapper(image) -> Phase:
            return image.addBands(Phase(coeff, mode))
        return wrapper
    
    def _add_amp(self, coeff, mode) -> Callable:
        def wrapper(image) -> Amplitude:
            return image.addBands(Amplitude(coeff, mode))
        return wrapper
    
    def _add_amps_phases(self, model: model, input_col: ee.ImageCollection):
        """
        Creates Phase and Amplitude images for each mode defined in the model and adds them to
        to each image in the input collection
        """
        fitted = input_col
        for mode in model.modes:
            fitted = fitted.map(self._add_amp(model.coefficients, mode)).\
                map(self._add_phase(model.coefficients, mode))
        return fitted

    def get_fourier_image(self, aoi: ee.Geometry = None) -> FourierImage:
        incol = self.fit.filterBounds(aoi) if aoi is not None else self.fit
        return FourierImage(incol)

    def get_collection(self, aoi: ee.Geometry = None):
        outcol = self.fit.map(lambda _: _.unitScale(-1, 1))
        return outcol.filterBounds(aoi) if aoi is not None else outcol

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#



def add_ndvi(nir: str, red: str) -> Callable:
    def add_ndvi_wrapper(element: ee.Image):
        return element.addBands(element.normalizedDifference([nir, red]).rename('NDVI'))
    return add_ndvi_wrapper


def add_constant(element: ee.Image):
    return element.addBands(ee.Image(1))


def add_time(omega: float = 1.5) -> Callable:
        def add_time_inner(image: ee.Image):
            date = image.date()
            years = date.difference(ee.Date('1970-01-01'), 'year')
            time_radians = ee.Image(years.multiply(2 * omega * math.pi))
            return image.addBands(time_radians.rename('t').float())
        return add_time_inner


def fit(model: model) -> ee.ImageCollection:
    def fit_wrapper(image: ee.Image):
        return image.addBands(image.select(model.independent).multiply(model.coefficients)\
            .reduce('sum').rename('fitted'))
    return model.harmonics.map(fit_wrapper)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def fourier(ee_object: ee.ImageCollection, modes: int = 5, omega: float = 1.5, nir: str = None, 
            red: str = None) -> FourierImage:
    """Applys fourier transform to defined image collection. Image Collection needs to be filtered 
    by start and end date, as well have a cloud mask applied. It also needs to have NDVI band in the 
    stack

    Args:
        ee_object (ee.ImageCollection): Optical Image Collection to have fourier transform fitted to
        modes (int, optional): number of modes to include. Defaults to 5.
        omega (float, optional): _description_. Defaults to 1.5.
    """
    # construct the input collection
    nir = "B8" if nir is None else nir
    red = "B4" if red is None else red
    
    # TODO add date minMax checker, if greater than 365 days use omega of 1
    
    time_series = ee_object.map(add_ndvi(nir=nir, red=red))\
        .map(add_constant)\
        .map(add_time(omega=omega))\

    fourier_model = model(
        ee_object=time_series,
        modes=modes,
        dependent_var="NDVI"
    )
    return FourierImage(model=fourier_model, ee_image_collection=time_series)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 
def build_fourier_inputs(target_aoi: ee.Geometry, time_range: Tuple[str] = None, modes: int = 3,
                         omega: float = 1.0, variable: d._RasterCalculator = None) -> ee.Image:
    """ Does Fourier Transform on Sentinel - 2 image Collection for the defined target area """
    
    def mask_clouds(element: ee.Image):
        qa = element.select('QA60')
        cloudBitMask = 1 << 10
        cirrusBitMask = 1 << 11
        mask = qa.bitwiseAnd(cloudBitMask).eq(0)\
            .And(qa.bitwiseAnd(cirrusBitMask).eq(0))
        return element.updateMask(mask)
    
    # Set default paramaters
    DATES = (2017, 2022) if time_range is None else time_range
    OMEAG = None # TODO check time range if > 365 set 1.0
    VAR = d.NDVI() if variable is None else variable
    
    s2SR = ee.ImageCollection("COPERNICUS/S2_SR").filterBounds(target_aoi)\
        .filterDate(*DATES).filter('CLOUDY_PIXEL_PERCENTAGE < 20').map(mask_clouds)\
        .map(VAR)\
        .map(add_constant)\
        .map(add_time(omega=omega))\
        .select(VAR.NAME)
        
    # build harmonics model
    h_model = model(
        ee_object=s2SR,
        modes=modes,
        omega=omega,
        dependent_var=VAR.NAME
    )
    
    trans = FourierTransform(
        model=h_model,
        col=s2SR
    )
    
    return trans.get_fourier_image(aoi=target_aoi)
    
    
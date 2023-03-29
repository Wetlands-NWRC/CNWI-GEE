import math
from typing import List, Callable, Tuple
import ee


class model:    
    def __init__(self, ee_object: ee.ImageCollection, modes: int = 5, dependent_var: str = None) -> None:
        self.modes = list(range(1, modes + 1))
        self.cos_names = [f'cos_{ _ }' for _ in self.modes]
        self.sin_name = [f'sin_{ _ }' for _ in self.modes]
        self.independent = ['constant', 't', *self.sin_name, *self.cos_names]
        self.dependent = dependent_var
        self.harmonics = ee_object.map(add_harmonics(
            freq=self.modes,
            cos_names=self.cos_names,
            sin_names=self.sin_name
        ))
        
        self.trend = self.harmonics.select([*self.independent, dependent_var]).\
            reduce(ee.Reducer.linearRegression(**{
                'numX': len(self.config.independents),
                'numY': 1
            }))
        
        self.coefficients: ee.Image = self.trend.select('coefficients').\
            arrayFlatten([self.independent, ["coeff"]])

        ee_object = None


class Phase(ee.Image):
    
    def __init__(self, coeff: ee.Image, mode: int):
        super().__init__(self._calc(coeff, mode))
    
    @staticmethod
    def _calc(coeff, mode) -> ee.Image:
        sin, cos, name = f'sin_{mode}_coeff', f'cos_{mode}_coeff', f'phase_{mode}'
        return coeff.select(sin).atan2(coeff.select(cos)).rename(name)
         

class Amplitude(ee.Image):
    def __init__(self, coeff: ee.Image, mode: int):
        super().__init__(self._calc(coeff, mode), None)

    @staticmethod
    def _calc(coeff, mode) -> ee.Image:
        sin, cos, name = f'sin_{mode}_coeff', f'cos_{mode}_coeff', f'amp_{mode}'
        return coeff.select(sin).atan2(coeff.select(cos)).rename(name)
         

class FourierImage(ee.Image):
    
    def __init__(self, model: model, ee_image_collection: ee.ImageCollection):
        self.img_col = ee_image_collection
        self.coeff = model.trend.select('coefficients')
        self.model = model
        
        ##
        # Construction start here
        with_coeff = self._add_bands_names(self.coeff, self.img_col)
        fitted = self._add_amps_phases(
            modes=self.model.modes,
            col=self.img_col,
            coeff=self.coeff
        )
        
        # all bands that have coeff
        coeff_bands: ee.List = fitted.select("*._coeff")
        amp_bands = self._get_names("amp_")
        phase_bands = self._get_names("phase_")
        
        # combine all lists to a single list
        required_bands: ee.List = coeff_bands.cat(amp_bands).cat(phase_bands)
        
        super().__init__(fitted.select(required_bands).median().unitScale(-1, 1), None)


    def _add_bands_names(self, model, coeff, col):
        expand = coeff.arrayFlatten([model.independent, ['coeff']])
        prefixed = [f'{_}_coeff' for _ in model.independent]
        return col.map(lambda x: x.addBands(expand.select(prefixed)))
    
    def _add_phase(self, coeff, mode) -> Callable:
        def wrapper(image) -> Phase:
            return image.addBands(Phase(coeff, mode))
        return wrapper
    
    def _add_amp(self, coeff, mode) -> Callable:
        def wrapper(image) -> Amplitude:
            return image.addBands(Amplitude(coeff, mode))
        return wrapper
    
    def _add_amps_phases(self, modes: List[int], col: ee.ImageCollection, coeff: ee.Image):
        """
        Creates Phase and Amplitude images for each mode defined in the model and adds them to
        to each image in the input collection
        """
        for mode in modes:
            col.map(self._add_amp(coeff, mode)).\
                map(self._add_phase(coeff, mode))
        return col
        
    def _get_names(self, base: str, modes: List[str]):
        return ee.List(modes).map(lambda x: ee.String(base).cat(ee.Number(x).int()))
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def add_harmonics(freq: List[int], cos_names: List[str], sin_names: List[str]) -> Callable:    
    def add_harmonics_wrapper(element: ee.Image):
        frequencies = ee.Image.constant(freq)
        time = ee.Image(element).select('t')
        cosines = time.multiply(frequencies).cos().rename(cos_names)
        sines = time.multiply(frequencies).sin().rename(sin_names)
        return element.addBands(cosines).addBands(sines)
    return add_harmonics_wrapper


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
            red: str = None) -> Tuple[fourierimage, ee.ImageCollection]:
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
    
    phase_img = phase(fourier_model)
    amp_img = amplitude(fourier_model)
    mean_dep = meanDepdendent(dependent_var="NDVI")
    
    fourier_image = fourierimage(
        phase=phase_img,
        amplitude=amp_img,
        mean_dependant=mean_dep
    )
    
    fitted = fit(fourier_model)
    return fourier_image, fitted
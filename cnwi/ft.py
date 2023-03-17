import math
from typing import List, Callable, Tuple
import ee


class model:    
    def __init__(self, ee_object: ee.ImageCollection, modes: int = 5, dependent_var: str = None) -> None:
        
        frequencies = list(range(1, modes + 1))
        
        self.cos_names = [f'cos_{ _ }' for _ in frequencies]
        self.sin_name = [f'sin_{ _ }' for _ in frequencies]
        self.independent = ['constant', 't', *self.sin_name, *self.cos_names]
        self.dependent = dependent_var
        self.harmonics = ee_object.map(add_harmonics(
            freq=frequencies,
            cos_names=self.cos_names,
            sin_names=self.sin_name
        ))
        
        self.trend = self.harmonics.select([*self.independent, dependent_var]).\
            reduce(ee.Reducer.linearRegression(**{
                'numX': len(self.config.independents),
                'numY': 1
            }))
        
        self.coefficients: ee.Image = self.trend.select('coefficients').\
            arrayProject([0]).\
            arrayFlatten([self.independent])

        ee_object = None


class phase:
    def __new__(cls, model: model) -> ee.Image:
        def phase_helper(band1, band2):
              return model.coefficients.select(band1).atan2(model.coefficients.select(band2))\
                .unitScale(-math.pi, math.pi)
        
        image = ee.Image.cat(*[phase_helper(x,y) for x,y in zip(model.sin_names, 
                                                                 model.config.cos_names)])

        return image.select(image.bandNames(), [f'phase_{idx}' for idx, _ in 
                                                  enumerate(model.sin_names, start=1)])


class amplitude:
    def __new__(cls, model: model) -> ee.Image:
        def amplitude_helper(band1, band2) -> ee.Image:
            return model.select(band1).hypot(model.coefficients.select(band2)).multiply(5)
        
        stack = ee.Image.cat(*[amplitude_helper(x,y) for x,y in zip(model.sin_names, 
                                                                    model.cos_names)])
        
        band_names: ee.List = stack.bandNames()
        new_names = [f'amplitude_{idx}' for idx, _ in enumerate(model.sin_names, start=1)]
        return stack.select(band_names, new_names)


class meanDepdendent:
    def __new__(cls, model: model, dependent_var: str = None) -> ee.Image:
          return model.time_series.select(model.dependent).mean()\
            .rename(f'{model.dependent}_mean')


class fourierimage:
    def __new__(cls, phase: phase, amplitude: amplitude, mean_dependant: meanDepdendent) -> ee.Image:
        return ee.Image.cat(phase, amplitude, mean_dependant)


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
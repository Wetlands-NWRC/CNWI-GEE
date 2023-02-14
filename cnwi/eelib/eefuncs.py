from typing import Dict, List, Union

import ee

from eelib import deriv, sf, td


def co_register(this_image: ee.Image, ref_image: ee.Image, max_offset: float,
                patch_width: float = None, stiffness: float = 5.0):
    """Used to register one image to the reference image"""

    return this_image.register(
        **{
            'referenceImage': ref_image,
            'maxOffset': max_offset,
            'patchWidth': patch_width,
            'stiffness': stiffness
        }
    )


def despeckle(images: Union[ee.ImageCollection, ee.Image], filter: sf.Boxcar):
    """Applys a defined spatial filter to either a single image or an image
    collection. If an image collection is passed it will apply the filter to
    every image in the Image collection

    Args:
        images (Union[ee.ImageCollection, ee.Image]): _description_
        filter (_type_): _description_
    """

    def convolve_inner(element: ee.Image) -> ee.Image:
        return element.convolve(filter)

    if isinstance(images, ee.ImageCollection):
        return images.map(convolve_inner)

    else:
        return images.convolve(filter)


def batch_co_register(images: List[ee.Image], max_offset: float,
                      patch_width: float = None, stiffness: float = 5.0):
    """Pops the image at index one. This is the reference image that all other
    images will be referenced to. iterates over each image in the defined image
    list applying the eefuncs.co_register function to each image.

    Args:
        images (List[ee.Image]): _description_
        max_offset (float): _description_
        patch_width (float, optional): _description_. Defaults to None.
        stiffness (float, optional): _description_. Defaults to 5.0.
    """
    ref_image = images.pop(0)
    images = [co_register(i, ref_image, max_offset, patch_width, stiffness) for
              i in images]
    images.insert(0, ref_image)
    return images


def batch_despeckle(images: List[ee.Image], filter: sf.Boxcar):
    """applys a spatial filter to each image in the image list. Only works on
    list of images. Not Image Collection. If using image collection use the 
    eefuncs.despeckle function.

    Args:
        images (List[ee.Image]): _description_
        filter (sf.Boxcar): _description_

    Returns:
        _type_: _description_
    """
    return [despeckle(i, filter) for i in images]


def batch_create_ratio(images: List[ee.Image], numerator: str, denominator: str) -> List[deriv.Ratio]:
    return [deriv.Ratio(img, numerator, denominator) for img in images]


def batch_create_ndvi(images: List[ee.Image], nir: str = None, red: str = None) -> List[deriv.NDVI]:
    return [deriv.NDVI(img, NIR=nir, RED=red) for img in images]


def batch_create_savi(images: List[ee.Image], nir: str = None, red: str = None,
                      coef: float = 0.5) -> List[deriv.SAVI]:
    return [deriv.SAVI(image=img, NIR=nir, RED=red, coef=coef) for img in images]


def batch_create_tassel_cap(images: List[ee.Image], blue: str = None, red: str = None,
                            green: str = None, nir: str = None, swir_1: str = None,
                            swir_2=None) -> List[deriv.TasselCap]:

    bands = [deriv.TasselCap(image=img, blue=blue, red=red, green=green,
                             nir=nir, swir_1=swir_1, swir_2=swir_2)
             for img in images]

    return bands


def new_labels(training_data: Union[ee.FeatureCollection, td.TrainingData],
               labelcol: str = None, offset: int = None) -> Dict[str, Union[ee.FeatureCollection, ee.Dictionary]]:
    """Used to add integer values to training dataset, adds a new column to 
    feature collection called 'land_value'.

    Args:
        training_data (ee.FeatureCollection): _description_
        labelcol (str): _description_

    Returns:
        Dict[str, Union[ee.FeatureCollection, ee.Dictionary]]: _description_
    """
    str_labels = training_data.aggregate_array(labelcol).distinct().sort()
    size = str_labels.size()
    start = 0 if offset is None else 0 + offset
    end = size.subtract(1) if offset is None else size

    int_labels = ee.List.sequence(start, end)
    lookup = ee.Dictionary.fromLists(str_labels, int_labels)

    def generate_label(element: ee.Feature):
        land_cover = element.get(labelcol)
        label = lookup.get(land_cover)
        return element.set('land_value', label)

    training_data = training_data.map(generate_label)
    return {'dataset': training_data, 'lookup': lookup}


def add_geometry_prop(element: ee.Feature):
    """adds geometry property to feature"""
    return element.set('GEOJSONGEOM', element.geometry())


def add_xy_property(feature: ee.Feature):
    coords = feature.geometry().coordinates()
    x = coords.get(0)
    y = coords.get(1)
    return feature.set({'POINT_X': x, 'POINT_Y': y})


def restructure_point(element: ee.Feature):
    geom = ee.Geometry.Point([element.get('POINT_X', 'POINT_Y')])
    return element.setGeometry(geom)


def from_geometry(featureCollection: ee.FeatureCollection):
    """adds the geometry to feature from the .geometry property in the features 
    property"""

    props = list(featureCollection.first().getInfo().get('properties').keys())

    def add_geometry(element: ee.Feature) -> ee.Feature:
        props = {prop: element.get(prop) for prop in props}
        geom = props.pop('GEOJSONGEOM')
        return ee.Feature(geom, props)

    return featureCollection.map(add_geometry)


def insert_groupid(element: ee.Image):
    """ Inserts a new prop called groupid this is only valid for Sentinel - 1 
    images"""
    rel_orbit = ee.Number(element.get(
        'relativeOrbitNumber_start')).format("%d")
    x = ee.Number(element.geometry().centroid(
    ).coordinates().get(0)).format('%.2f')
    return element.set('groupid', ee.String(rel_orbit).cat("_").cat(x))


def get_mid_point(dateRange: tuple[ee.Date]) -> ee.Date:
    """ date range is assumed to be a tuple of ee.Date objects that represent
    a start date and an end date. It will find the mid point between the two dates
    and add that as a property to each image in the image Collection. this assumes
    that each image in the collection has a datetime property associated with it.
    """
    start, stop = dateRange
    mapping = {'start': start.millis(), 'stop': stop.millis()}
    equation = ee.Number.expression('start + (stop - start) / 2', mapping)

    return ee.Date(equation)


def days_from_mid(collection: ee.ImageCollection, midPoint: ee.Date, units: str = None):
    """ adds prop called dfm. the property reperesent the number of days that the 
    image is from the defined mid point

    the start and end dates of the input collection must intersect the midPoint 
    arg in order for this to work properly
    """

    units = 'days' if units is None else units

    def dfm_calc(element: ee.Image):
        dif = element.date().difference(midPoint, units).abs().floor()
        return element.set('dfm', ee.Number(dif))

    return collection.map(dfm_calc)


def moa_calc(samples: ee.FeatureCollection, predictors: ee.List,
             label_col: str, c1: str, c2: str) -> ee.List:

    c1q = f'{label_col} == "{c1}"'
    c2q = f'{label_col} == "{c2}"'
    query_str = f'{c1q} || {c2q}'

    def calc_inner(element):
        inputCol = samples.filter(query_str)

        std = inputCol.aggregate_total_sd(element)

        c1p1 = inputCol.filter(c1q)
        c2p1 = inputCol.filter(c2q)

        m1 = c1p1.aggregate_mean(element)
        m2 = c2p1.aggregate_mean(element)

        calc = ee.Number.expression('abs((m2 - m1) / std)', {
            "m1": m1,
            "m2": m2,
            "std": std
        })

        return calc
    values = predictors.map(calc_inner)
    zipped = predictors.zip(values)
    return zipped

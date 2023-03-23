from datetime import datetime
from typing import Union

import ee


# def parse_s1_imgs(collection: ee.ImageCollection):
#     dates: list[str] = collection.aggregate_array('date').getInfo()
   
#     if len(dates) > 3:
#         imgs = [collection.filter(f'date == "{date}"').mean().set('date', date)
#                for date in sorted(set(dates))]
#     else:
#         imgs = [ee.Image(_.get('id')).set('date', dates[idx]) for idx, _ 
#                 in enumerate(collection.toList(collection.size()).getInfo())]

#     return ImageList(imgs)


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


def create_rectangle(ee_object: Union[ee.FeatureCollection, ee.Geometry]) -> ee.Geometry:
    """Creates a rectangle from a Feature Collection of Geometry"""
    if isinstance(ee_object, ee.FeatureCollection):
        geom = ee_object.geometry()
    else:
        geom = ee_object

    coords = geom.bounds().coordinates()

    listCoords = ee.Array.cat(coords, 1)
    xCoords = listCoords.slice(1, 0, 1)
    yCoords = listCoords.slice(1, 1, 2)

    xMin = xCoords.reduce('min', [0]).get([0, 0])
    xMax = xCoords.reduce('max', [0]).get([0, 0])
    yMin = yCoords.reduce('min', [0]).get([0, 0])
    yMax = yCoords.reduce('max', [0]).get([0, 0])

    return ee.Geometry.Rectangle(xMin, yMin, xMax, yMax)

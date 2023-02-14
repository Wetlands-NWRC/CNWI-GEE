import ee
import folium


class eeMapper(folium.Map):
    def __init__(self, location=None, width='100%', height='100%', left='0%',
                 top='0%', position='relative', tiles='OpenStreetMap',
                 attr=None, min_zoom=0, max_zoom=18, zoom_start=10, min_lat=-90,
                 max_lat=90, min_lon=-180, max_lon=180, max_bounds=False,
                 crs='EPSG3857', control_scale=False, prefer_canvas=False,
                 no_touch=False, disable_3d=False, png_enabled=False,
                 zoom_control=True, **kwargs):

        super().__init__(location, width, height, left, top, position, tiles,
                         attr, min_zoom, max_zoom, zoom_start, min_lat, max_lat,
                         min_lon, max_lon, max_bounds, crs, control_scale,
                         prefer_canvas, no_touch, disable_3d, png_enabled,
                         zoom_control, **kwargs)

    def add_ee_layer(self, ee_image_object, vis_params, name):
        if isinstance(ee_image_object, ee.ImageCollection):
            map_id_dict = ee.Image(
                ee_image_object.mosaic()).getMapId(vis_params)

        elif isinstance(ee_image_object, ee.FeatureCollection):
            map_id_dict = ee.FeatureCollection(
                ee_image_object).getMapId(vis_params)

        else:
            map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)

        folium.raster_layers.TileLayer(
            tiles=map_id_dict['tile_fetcher'].url_format,
            attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
            name=name,
            overlay=True,
            control=True
        ).add_to(self)

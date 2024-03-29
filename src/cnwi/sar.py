import ee

from . import derivatives as d
from . import sfilters as s


class Sentinel1(ee.ImageCollection):
    ARGS = "COPERNICUS/S1_GRD"
    
    def __init__(self):
        """ Constructs a Image Collection that Represents a collecton of Sentinel 1 Images """
        super().__init__(self.ARGS)
    
    def get_s1dv_collection(self, aoi: ee.Geometry, date: tuple[str]) -> ee.ImageCollection:
        return self.filterBounds(aoi).filterDate(*date)\
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))\
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))\
            .filter(ee.Filter.eq('instrumentMode', 'IW'))


class ALOS(ee.ImageCollection):
    ARGS = "JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH"

    def __init__(self):
        super().__init__(self.ARGS)


def build_alos_inpts(target_yyyy: int) -> ee.Image:
    mosaic: ee.Image = ALOS().filterDate(f'{target_yyyy}', f'{target_yyyy + 1}').select('H.*').first()
    
    ratio = d.Ratio(
        numerator='HH',
        denominator='HV'
    )
    
    with_ratio = ratio.calculate(mosaic)
    return with_ratio


def build_s1_inputs(col: ee.ImageCollection) -> ee.Image:
    EARLY_SEASON = '2019-04-01', '2019-06-20'
    LATE_SEASON = '2019-06-21', '2019-10-31'
    
    # select only VV and VH
    in_col = col.select('V.*')
    # apply spatial filter
    boxcarf = s.boxcar(1)
    s1_pp1 = in_col.map(boxcarf)
    # add ratio
    ratio = d.Ratio('VV', 'VH')
    s1_pp2 = s1_pp1.map(ratio)
    # sperate into early and late season
    early = s1_pp2.filterDate(*EARLY_SEASON)
    late = s1_pp2.filterDate(*LATE_SEASON)
    # mosaic early and late
    early_mosaic = early.mosaic()
    late_mosaic = late.mosaic()
    # concat early and late into one image
    return ee.Image.cat(early_mosaic, late_mosaic)


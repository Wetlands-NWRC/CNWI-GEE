import ee

from . import derivatives as d
from . import sfilters as s


class Sentinel1(ee.ImageCollection):
    ARGS = ""
    
    def __init__(self):
        """ Constructs a Image Collection that Represents a collecton of Sentinel 1 Images """
        super().__init__(self.ARGS)    


class ALOS(ee.ImageCollection):
    ARGS = "JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH"

    def __init__(self):
        super().__init__(self.ARGS)


def build_alos_inpts(target_yyyy: int) -> ee.Image:
    mosaic: ee.Image = ALOS.filterDate(f'{target_yyyy}', f'{target_yyyy + 1}').select('H.*').first()
    
    ratio = d.Ratio(
        numerator='HH',
        denominator='HV'
    )
    
    with_ratio = ratio.calculate(mosaic)
    return with_ratio


def build_s1_inputs(col: ee.ImageCollection) -> ee.Image:
    EARLY_SEASON = '04-01', '06-20'
    LATE_SEASON = '06-21', '10-31'
    
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
    return ee.Image.concat(early_mosaic, late_mosaic)
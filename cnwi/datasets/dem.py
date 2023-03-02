from typing import Callable

import ee


class CDEM(ee.ImageCollection):
    _ASSET_ID = "NRCan/CDEM"
    
    def __init__(self):
        super().__init__(self._ASSET_ID)


class SRTMV3(ee.Image):
    _ASSET_ID = "USGS/SRTMGL1_003"
    
    def __init__(self):
        super().__init__(self._ASSET_ID, None)


class NASADEM_HGT(ee.Image):
    _ASSET_ID = "NASA/NASADEM_HGT/001"

    def __init__(self):
        super().__init__(self._ASSET_ID)
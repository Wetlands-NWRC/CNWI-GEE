from typing import Callable

import ee


class CDEM(ee.ImageCollection):
    _ASSET_ID = "NRCan/CDEM"
    
    def __init__(self):
        super().__init__(self.ASSET_ID)
    
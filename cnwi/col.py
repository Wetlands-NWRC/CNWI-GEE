from abc import ABC
import ee


class _ImageCollection(ee.ImageCollection):
    ARGS: str
    
    @classmethod
    def show_constructor(cls):
        return cls.ARGS
    
    def __init__(self):
        super().__init__(self.ARGS)


class ALOSCollection(_ImageCollection):
    ARGS: str = "JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH"
    def __init__(self):
        """_summary_
        """
        super().__init__()


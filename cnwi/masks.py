import ee
from . import inputs

class AAFCCropMask:
    #@TODO make it able to take multiple values 
    def __new__(cls, values: tuple[int] = 80, target_year: int = 2018) -> ee.Image:
        aafc = inputs.AAFC(target_year=target_year, viewport=None)
        base = "aadc.neq(neq)"
        ands = [f'.and(aafc.neq(val))' for val in values]
        mask = aafc.neq(neq)

        for cond in ands:
            base += cond
        
        update_mask: ee.Image = eval(base)
        
        return update_mask 
from abc import ABC
import ee

class Mask(ABC):
    def __init__(self, product: ee.Image) -> None:
        self.product = product 
        super().__init__()
    
    
    def get_mask(self):
        pass


class SlopeMask(Mask):
    def __init__(self, product: ee.Image, deg: int = 15) -> None:
        super().__init__(product)
        self.deg = deg
    def get_mask(self, deg: int = 15) -> ee.Image:
        """returns an image where everything less than or equal to the deg has been selects"""
        return self.product.lte(self.deg)


class CropMask(Mask):
    def _mk_expression(self, values: list[int]):
        """helper function to create an expression"""
        base=f"crop.neq({values.pop(0)})"
        and_exp = ".And(crop.neq({value}))"
        for value in values:
            base+=and_exp.format(value=value)
        return base
    
    def get_mask(self) -> ee.Image:
        """Creates a Crop mask"""
        # TODO need to document crop values, and find a way to iterativly isolate the values to be 
        # masked out
        # Might need to create an expression that represents 
        crop = self.product
        return crop.neq(80).And(crop.neq(200)).And(crop.neq(210)).And(crop.neq(220))\
            .And(crop.neq(230))


def update_mask(image: ee.Image, mask: Mask) -> ee.Image:
    return image.updateMask(mask.get_mask())
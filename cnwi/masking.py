from abc import ABC
import ee

class Mask(ABC):
    def __init__(self, product: ee.Image) -> None:
        self.product = product 
        super().__init__()
    
    
    def get_mask(self):
        pass


class SlopeMask(Mask):    
    def get_mask(self, deg: int = 15) -> ee.Image:
        """returns an image where everything less than or equal to the deg has been selects"""
        return self.product.lte(deg)


class CropMask(Mask):
    def get_mask(self) -> ee.Image:
        """Creates a Crop mask"""
        # TODO need to document crop values, and find a way to iterativly isolate the values to be 
        # masked out
        # Might need to create an expression that represents 
        return super().get_mask()


def update_mask(image: ee.Image, mask: Mask) -> ee.Image:
    return image.updateMask(mask.get_mask())
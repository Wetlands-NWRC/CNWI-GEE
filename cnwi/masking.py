import ee

class Mask(ABC):
    product: ee.Image
    
    def get_mask(self):
        pass


class SlopeMask:    
    def get_mask(self, deg: int = 15) -> ee.Image:
        """returns an image where everything less than or equal to the deg has been selects"""
        return self.slope.lte(self.deg)


def update_mask(image: ee.Image, mask: Mask) -> ee.Image:
    return image.updateMask(mask.get_mask())
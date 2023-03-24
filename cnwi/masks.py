import ee


def slope_mask(slope: ee.Image, deg: int = 15):
    return slope.lte(deg)

    
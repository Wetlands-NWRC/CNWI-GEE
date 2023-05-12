import ee
import eecnwi


def test_build_data_cube_inputs() -> None:
    ARGS = "projects/fpca-336015/assets/NovaScotia/data_cube"
    AOI = ee.FeatureCollection("projects/fpca-336015/assets/NovaScotia/_527_ECO_DIST").geometry()
    
    dc = eecnwi.build_data_cube(
        arg=ARGS,
        aoi=AOI
    )
    
    print(dc.bandNames().getInfo())


def test_build_alos_inputs() -> None:
    alos = eecnwi.build_alos()
    print(alos.bandNames().getInfo())    
    return None


if __name__ == '__main__':
    ee.Initialize()
    test_build_alos_inputs()
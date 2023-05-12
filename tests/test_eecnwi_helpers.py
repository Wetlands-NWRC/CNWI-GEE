import ee
import eecnwi

ee.Initialize()
AOI = ee.FeatureCollection("projects/fpca-336015/assets/NovaScotia/_527_ECO_DIST").geometry()


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


def test_build_elevation_prebuilt() -> None:
    terrain_analysis = eecnwi.build_elevation(
        arg="projects/fpca-336015/assets/NovaScotia/terrain_analysis",
        aoi=AOI
    )
    print(terrain_analysis.bandNames().getInfo())
    return None


def test_build_fourier_transform_prebuilt() -> None:
    fourier_transform = eecnwi.build_fourier_transform(
        arg="projects/fpca-336015/assets/NovaScotia/fourier_transform",
        aoi=AOI
    )
    print(fourier_transform.bandNames().getInfo())
    return None

if __name__ == '__main__':
    test_build_fourier_transform_prebuilt()
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


def test_build_stack() -> None:
    dc_arg = "projects/fpca-336015/assets/NovaScotia/data_cube" 
    dc = eecnwi.build_data_cube(
        arg=dc_arg,
        aoi=AOI
    )
    
    alos = eecnwi.build_alos()
    
    terrain_analysis = eecnwi.build_elevation(
        arg="projects/fpca-336015/assets/NovaScotia/terrain_analysis",
        aoi=AOI
    )
    
    fourier_transform = eecnwi.build_fourier_transform(
        arg="projects/fpca-336015/assets/NovaScotia/fourier_transform",
        aoi=AOI
    )
    
    stack = eecnwi.build_stack(dc, alos, terrain_analysis, fourier_transform)
    print(stack.bandNames().getInfo())
    return None


def test_build_s1_inputs():
    s1_dv = eecnwi.build_sentinel1(
        aoi=AOI
    )
    print(s1_dv.bandNames().getInfo())


if __name__ == '__main__':
    test_build_s1_inputs()
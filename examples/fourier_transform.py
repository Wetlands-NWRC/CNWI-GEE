import ee
from cnwi import ft, prebuilt


def cloud_mask(element: ee.Image) -> ee.Image:
    qa = element.select('QA60')
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 11
    mask = qa.bitwiseAnd(cloudBitMask).eq(0).And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    return element.updateMask(mask)


def main():
    start_yyyy = 2018
    end_yyyy = 2019
    
    aoi = ee.FeatureCollection("users/ryangilberthamilton/BC/williston/williston_sub_a_2019")

    s2_collection = prebuilt.Sentinel2SR().filterBounds(aoi).filterDate(f"{start_yyyy}", f"{end_yyyy}").\
        map(cloud_mask)

    fourier_image = ft.fourier(
        ee_object=s2_collection,
        omega=1
    )
    
    print(fourier_image.bandNames().getInfo())

if __name__ == '__main__':
    ee.Initialize()
    main()
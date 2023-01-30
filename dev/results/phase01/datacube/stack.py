import ee
from pipelines import factories


def main():
    s1ids = [
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180517T142651_20180517T142716_010962_014115_CA58",
        "COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180728T142655_20180728T142720_012012_0161D6_96BF"
    ]
    s2ids = [
        "COPERNICUS/S2/20180519T191909_20180519T192621_T10UEF",
        "COPERNICUS/S2/20180728T191909_20180728T192508_T10UEF"
    ]

    viewport = ee.FeatureCollection("users/ryangilberthamilton/BC/williston/williston_sub_a_2019").\
        geometry()
    s1_imgs = factories.s1_factory(s1ids)
    s2_imgs = factories.s2_factory(s2ids)

    stack = ee.Image.cat(*s1_imgs, *s2_imgs).float()
    data = ee.FeatureCollection(
        "users/ryangilberthamilton/BC/williston/subset_a_good")

    samples = stack.sampleRegions(
        collection=data,
        scale=10,
        tileScale=8,
        geometries=True
    )

    ee.batch.Export.table.toDrive(
        collection=samples,
        description="samples-from-stack",
        folder='test_stacking',
        fileFormat='SHP'
    ).start()

    # tasks_cfg = {
    #     'image': stack,
    #     'description': None,
    #     'region': viewport,
    #     'scale': 10,
    #     'folder': 'test_stacking',
    #     'maxPixels': 1e13
    # }

    # w_crs = tasks_cfg
    # w_crs['crs'] = 'EPSG:4326'
    # w_crs['description'] = 'stack-with-crs'

    # ee.batch.Export.image.toDrive(**w_crs).start()

    # w_out_crs = tasks_cfg
    # w_out_crs['description'] = 'stack-without-crs'
    # ee.batch.Export.image.toDrive(**w_out_crs).start()


if __name__ == "__main__":
    main()

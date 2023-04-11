from dataclasses import dataclass, field

@dataclass(frozen=True)
class WillistonA:
    s1: list = field(default_factory=lambda: [
        'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180517T142651_20180517T142716_010962_014115_CA58',
        'COPERNICUS/S1_GRD/S1B_IW_GRDH_1SDV_20180728T142655_20180728T142720_012012_0161D6_96BF'
    ])
    s2: list = field(default_factory=lambda: [
        'COPERNICUS/S2_HARMONIZED/20180519T191909_20180519T192621_T10UEF',
        'COPERNICUS/S2_HARMONIZED/20180728T191909_20180728T192508_T10UEF'
    ])
    region: str = "users/ryangilberthamilton/BC/williston/williston_sub_a_2019"
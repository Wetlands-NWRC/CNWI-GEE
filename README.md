# CNWI-GEE
Canadian National Wetland Inventory Google Earth Engie Random Forest Classifications

# CNWI - work flow 
- 2 Potnetial Inputs GEE native and Data Cube
- load vector data
    - viewport (region on which we want to export)
    - training data
# Pipeline Steps

# Phase 05
- Start to simulate what the final product is going to look like
- Create an Eco district gdb
    - eco districts
    - training data
- provide an eco district
    - phase 5 target is 970
    - pull all information that corresponds to the target eco district
- implement a point balancer tool
    - all data prep will be done outside of Earth Engine API using geopandas
    - function that takes a geo data frame as an argument
    - calc summary stats i.e. class counts
    - if the data set is not balanced, map a random index based on the class counts. 
    - slice the data frame do the limiting class i.e. select all classes less than or equal to the 
        class that has the least amount
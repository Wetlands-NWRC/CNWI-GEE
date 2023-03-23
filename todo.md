# TODO

# CNWI-GEE v1.0.6
- Updates to DEM
  - [] Update default DEM to be NASA DEM
- DEM Processing
  - [x] By Default Terrain Analysis output bands 1 - 3 need to be Guassien filter
  - [x] 4-6 need to be Perona Malik Filter
- General Updates
  - [x] Create create_rectangle function creates rectangle from feature collection or geometry -> put into eefuncs 
  - [] Make it so the pipeline can run with only certain products ex = Optical and not SAR, DEM and not SAR etc 

# CNWI - GEE v1.0.8
Major update. Will be refactoring and simplifying the package, and organizing it.
## Things that need to be done for refactor
- [] remove eelib / move functionality
  - [] deriv 
    - [] simplify, move from classes to functions
    - [] rename to derivatives
    - [] move to top level
  - [] eefuncs
    - [] move to toplevel, to replace funcs
    - [] move parsers to eefuncs module
  - [] sf 
    - [] rename to sfilters
    - [] move to toplevel
    = [] boxcar filter create function
    - [] remove wrappers, doesnt make sense for the time being
  - [] move MOA table and calc to seperate repo / project
  - []


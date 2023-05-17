# TODO
1) Work on sentinel-1 time series tool to get canidate images for classification
2) Work on moa tool
3) implement data sturcture to store image tiles 
4) move fourier transform generation to external tool
5) Move terrain analysis to seperate tool
6) prep training data tool to work on client  
7) top level helper functions (Done)
8) need to add asset creation tooling i.e for moving things from gcp to gee
----------------------------------------------------------------------
# TODO v0.0.2
- [x] add script tool for prepping training / validation data
- [ ] add internal main script for doing standard random forest classification
- [ ] add fourier transform script tool (to start); standard way of preforming the export
- [ ] add terrain analysis script tool; standard way of exporting terrain analysis products
- [ ] put fourier transform into its own sub module
- [ ] work on cli functionality for project / custom pipeline utils
- [ ] need to role back to 4.0.1 release. There is a unknown problem with exporting classification images (they get messed up)
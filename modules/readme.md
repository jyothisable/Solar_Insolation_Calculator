# Modules
* initialize(raster) => Input DEM and find horizon, slope and aspect (only need once per location and resolution)
* RMSPE(sumRaster, counter) => find root mean percentage square error using comparison error raster (comp) map cleated during validation
* 
These modules forms a higher level abstraction for native GRASS GIS functions.
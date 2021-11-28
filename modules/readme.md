# Modules

- initialize => Input DEM and find horizon, slope and aspect (only need once per location and resolution)
- calcInsolation => For a day and time returns calculated solar insolation raster as string name in GRASS GIS
- validate => Validate above found raster with satellite data and find error raster and its sum as sumRaster
- RMSPE => Find root mean square percentage error using sumRaster raster cleated during validation
- outputStats => Output statistics of raster file
- outputFiles => Output raster file as .tif and .png
- datetime => nth day of the year and IST time to DDMMMYYYY_HHMM (HHMM in UTC)

These modules forms a higher level abstraction for native GRASS GIS functions. To know more about these function visit [GRASS GIS documentation](https://grass.osgeo.org/grass78/manuals/index.html)

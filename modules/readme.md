# Modules

- initialize => Input DEM and find horizon, slope and aspect
- calcInsolation => For a day and time returns calculated solar insolation raster as string name in GRASS GIS
- validate => Validate above found raster with satellite data and find error raster and its sum as sumRaster
- RMSPE => Find root mean square percentage error using sumRaster raster cleated during validation
- outputStats => Output statistics of raster file
- outputFiles => Output raster file as .tif and .png
- datetime => nth day of the year and IST time to DDMMMYYYY_HHMM (HHMM in UTC)

These modules forms a higher level of abstraction for native GRASS GIS functions. To know more about GRASS GIS function visit [documentation](https://grass.osgeo.org/grass78/manuals/index.html)

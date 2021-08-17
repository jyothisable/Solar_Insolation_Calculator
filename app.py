#!/usr/bin/env conda run -n MTP python
# =============================================================================
# Created By  : Athul Jyothis
# Created Date: 18-08-2021 00:17:21
# =============================================================================
"""
The module has been build for calculating the solar insolation of a region using DEM (digital elevation modlel)
using grass gis r.sun module
"""
import grass.script as gs
import os

def calculate(dem_input,day,time):
    '''
    inputs
    dem_input: string name of DEM file 
    day:integer [1-365]
    time:integer [1-24]
    output : Solar insolation as raster (.tif) file
    '''
    gs.run_command('g.region', raster=dem_input)
    os.chdir('data/input_DEMs'); 
    gs.run_command('r.sun', elevation=dem_input, horizon_basename=(dem_input)+'_horangle', horizon_step=30, aspect=(dem_input)+'_aspect.dem',
                   slope=(dem_input)+'_slope.dem', glob_rad=(dem_input)+'_solar_insolation', day=day, time=time, linke_value=1, nprocs=6, overwrite=True)
    os.chdir('../output'); 
    gs.run_command('r.out.gdal', input=(dem_input)+'_solar_insolation',
                   output=(dem_input)+'_output'+'.tif', type='Float64', overwrite=True)

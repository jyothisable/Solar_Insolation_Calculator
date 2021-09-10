#!/usr/bin/env conda run -n MTP python3
# =============================================================================
# Created By  : Athul Jyothis
# Created Date: 18-08-2021 00:17:21
# =============================================================================
"""
The module has been build for calculating the solar insolation of a region using DEM (digital elevation model)
using grass gis
#Importnet
clear output data folder manually before running again
use new mapset for new input dem because horizon doesn't overwrite
"""

import os
from pathlib import Path
import csv
import grass.script as gs
from datetime import datetime as d
# change directory because the file is usually imported to grass gis
os.chdir(os.path.dirname(__file__))


def findSolarInsolation(day=30, time=12):
    '''
    inputs the day and time to find solar insolation for all the files present in input_DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''
    files = Path('data/input_DEMs').glob('*.tif')
    for file in files:
        gs.run_command('r.in.gdal', input=file,
                       output='DEM', overwrite=True)
        gs.run_command('r.horizon', elevation='DEM', step=7.5,
                       output='horangle')
        gs.run_command('r.slope.aspect', elevation='DEM',
                       aspect='aspect.dem', slope='slope.dem', overwrite=True)
        # solar time only applicable for this data set => need to change #todo find a module to calc this
        solar_time = time - 1
        gs.run_command('r.sun', elevation='DEM', horizon_basename='horangle',
                       horizon_step=7.5, aspect='aspect.dem', slope='slope.dem',
                       glob_rad='global_rad', day=day, time=solar_time, nprocs=6, linke_value=5,
                       albedo_value=0.4, overwrite=True)

        res = 0.0376967592499995625  # specific to this case
        gs.run_command('r.resamp.interp', input='global_rad',
                       output='DEM_upscaled', overwrite=True)
        # output results stats into CSV (can't append directly)
        gs.run_command('r.univar', map='DEM_upscaled',
                       output='data/cache/stats_cache.csv', separator='comma', overwrite=True, flags='te')

        # copy and append to a permanent stats.csv file
        with open('data/cache/stats_cache.csv', newline='') as cache_csv:
            lastLine = cache_csv.read().splitlines()[-1]
        fileName = os.path.basename(file).split('.')[0]
        with open('data/output/' + fileName + '_stats.csv', 'a') as output_csv:
            if os.stat('data/output/' + fileName + '_stats.csv').st_size == 0:
                output_csv.writelines(
                    'day,time,non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90')
            output_csv.write("\n")
            output_csv.writelines(str(day)+','+str(time)+','+lastLine)

        gs.run_command('r.out.gdal', input='DEM_upscaled',
                       output='data/output/'+fileName + '_D'+str(day)+'_H'+str(time)+'.tif', type='Float64', overwrite=True)


# specify range of day [1-365 int] and time [24h float]
for day in range(1, 32):
    for time in range(22, 31):  # 11am to 3pm
        findSolarInsolation(day, time/2)

#!/usr/bin/env python3
# # =============================================================================
# Created By  : Athul Jyothis
# Created Date: 18-08-2021 00:17:21
# =============================================================================
"""
The module has been build for calculating the solar insolation of a region using DEM (digital elevation model)
using grass gis
#Important note
clear csv files in output data folder manually before running again (otherwise it would append)
"""
from modules.calcInsolation import calcInsolation
from modules import datetime
from modules.validate import validate
from modules.outputFile import outputFile
from modules.outputStats import outputStats
from modules.

import os
from pathlib import Path
import grass.script as gs
from datetime import datetime as d
# change directory because this file is usually imported to grass gis
# os.chdir(os.path.dirname(__file__))  #todo importing not working in linux
# Temperory fix : given absolute path to the this file below and just copy paste the code to grass gis (importing not working in linux)
os.chdir('/home/jyothisable/P.A.R.A/1.Projects/mtp/Softwares/VS code/Solar_Insolation_Calculator')

file = 'data/inputs/DEMs/jamnagar_32m_clipped.tif'
gs.run_command('r.in.gdal',
               input=file,
               output='DEM',
               overwrite=True)


# deg: Km
# 0.03455: '4km',
# 0.0086375: '1km',
# 0.002159375: '0.25km',
# 0.0002714 : '0.03km',

res = {
    0.0086375: '1km',
    0.0002714: '0.03km',
    0.002159375: '0.25km',
}

for res_deg, res_m in res.items():
    gs.run_command('g.region',
                   raster='DEM',
                   #    vector='ref_vector',
                   res=res_deg)

    gs.run_command('r.horizon',
                   elevation='DEM',
                   step=1,
                   output='horangle')
    gs.run_command('r.slope.aspect',
                   elevation='DEM',
                   aspect='aspect.dem',
                   slope='slope.dem',
                   overwrite=True)

    counter = 1
    # specify range of day [1-365 int] and time [24h float]
    for day in range(1, 83):
        # 11:30am to 3:30pm IST (6 to 10 UTC)=> about 11 to 3pm solar time
        for time in range(23, 29):
            time = time/2
            formatedDT = datetime.convert(day, time)
            insolation = calcInsolation(formatedDT)
            sumRaster = validate(insolation, formatedDT, counter)
            outputCSV_Loc = 'data/outputs/' + res_m + \
                '/' + res_m + '_' + 'jamnagar' + '_stats.csv'
            outputFile_loc = 'data/outputs/' + res_m + '/' + res_m + '_' + 'jamnagar' +
            '_D'+str(day)+'_H'+str(time)+'.tif'
            outputStats(outputCSV_Loc,insolation)
            outputFile(outputFile_loc,insolation)
            counter += 1
    RMPSE(sumRaster)

res = {
    0.0086375: '1km',
    0.0002714: '0.03km',
    0.002159375: '0.25km',
}

for res_deg, res_m in res.items():
    gs.run_command('g.region',
                   raster='DEM',
                   #    vector='ref_vector',
                   res=res_deg)

    gs.run_command('r.horizon',
                   elevation='DEM',
                   step=1,
                   output='horangle')
    gs.run_command('r.slope.aspect',
                   elevation='DEM',
                   aspect='aspect.dem',
                   slope='slope.dem',
                   overwrite=True)

    counter = 0
    # specify range of day [1-365 int] and time [24h float]
    for day in range(1, 83):
        # 11:30am to 3:30pm IST (6 to 10 UTC)=> about 11 to 3pm solar time
        for time in range(23, 29):
            t = time/2
            counter += 1

            solar_time = t - 1.221986 + 0.008938792*day - \
                0.0001198693 * day**2 + 2.464719e-7*day**3

            findSolarInsolation(day, t)

    # take average of comp_timeAvg with counter
    gs.run_command('r.mapcalc.simple',
                   a='comp_timeAvg',
                   expression='result = sqrt(A/' + str(counter) + ')',
                   output='comp_timeAvg',
                   overwrite=True)
    gs.run_command('r.univar',
                   map='comp_timeAvg',
                   output='data/.cache/stats_cache.csv',
                   separator='comma',
                   flags='te',
                   overwrite=True)
    with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/outputs/' + res_m + '_validation' +
              '/' + res_m + '_timeAvg_stats.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '_validation' +
                   '/' + res_m + '_timeAvg_stats.csv').st_size == 0:
            output_csv.writelines(
                "non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(lastLine)

    # export comp_timeAvg as tif
    gs.run_command('r.out.gdal',
                   input='comp_timeAvg',
                   output='data/outputs/' + res_m + '_validation' +
                   '/' + res_m + '_timeAvg_validation.tif',
                   overwrite=True)
    # remove comp_timeAvg raster
    gs.run_command('g.remove',
                   type='raster',
                   name='comp_timeAvg')

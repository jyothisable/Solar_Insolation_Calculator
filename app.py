#!/usr/bin/env conda run -n MTP python3
# =============================================================================
# Created By  : Athul Jyothis
# Created Date: 18-08-2021 00:17:21
# =============================================================================
"""
The module has been build for calculating the solar insolation of a region using DEM (digital elevation model)
using grass gis r.sun module
"""

import os
import csv
import grass.script as gs
os.chdir(os.path.dirname(__file__))


def findSolarInsolation(path='data/input_DEMs/IIT_Bbs_DEM.tif', day=30, time=11):
    gs.run_command('r.in.gdal', input=path,
                   output='DEM', overwrite=True)
    gs.run_command('r.horizon', elevation='DEM', step=7.5,
                   output='horangle')
    gs.run_command('r.slope.aspect', elevation='DEM',
                   aspect='aspect.dem', slope='slope.dem', overwrite=True)
    gs.run_command('r.sun', elevation='DEM', horizon_basename='horangle',
                   horizon_step=7.5, aspect='aspect.dem', slope='slope.dem',
                   glob_rad='global_rad', day=30, time=11, nprocs=6, linke_value=5,
                   albedo_value=0.4, overwrite=True)
    gs.run_command('r.univar', map='global_rad',
                   output='data/cache/stats_cache.csv', separator='comma', overwrite=True, flags='te')

    with open('data/cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/output/stats.csv', 'a') as output_csv:
        output_csv.write("\n")
        output_csv.writelines(lastLine)


findSolarInsolation()
# r.horizon elevation = desert step = 30 output = horangle - -overwrite
# r.slope.aspect elevation = desert aspect = aspect.dem slope = slope.dem - -overwrite
# r.sun elevation = desert horizon_basename = horangle horizon_step = 30 aspect = aspect.dem slope = slope.dem glob_rad = global_rad day = 30 time = 11 nprocs = 4 linke_value = 5 albedo_value = 0.4 - -overwrite
# r.univar global_rad
# d.mon wx0
# d.rast.leg global_rad
# r.out.gdal input = global_rad output = desert_output.tif - -overwrite

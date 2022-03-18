#!/usr/bin/env python3
# # =============================================================================
# Created By  : Athul Jyothis
# Created Date: 18-08-2021 00:17:21
# =============================================================================
"""
The module has been build for calculating the solar insolation of a region using DEM (digital elevation model)
using grass gis
# Important note
clear csv files in output data folder manually before running again (otherwise it would append)
"""
import os
from pathlib import Path
import grass.script as gs
from datetime import datetime as d
import random
# change directory because this file is usually imported to grass gis
# os.chdir(os.path.dirname(__file__))  #todo importing not working in linux
# Temperory fix : given absolute path to the this file below and just copy paste the code to grass gis (importing not working in linux)
os.chdir('/home/athul/Solar_Insolation_Calculator')


def findSolarInsolation(day, time):
    '''
    inputs the day and time to find solar insolation for Digital Elevation model present in inputs/DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''
    # assigning region => default boundary and location
    gs.run_command('g.region',
                   raster='DEM',
                   rows=208,
                   cols=304)

    # convert time format  # todo use datetime module to do this
    t = int(time*100)-550
    min = str(int(((t % 100)/100)*60))
    if min == '0':
        min = '00'
    time_UTC = '0'+str(t//100) + min if t//100 < 10 else str(t//100) + min

    d = int(day)
    if d <= 31:
        d = str(d) + 'JAN'
    elif d <= 60:
        d = str(d - 31) + 'FEB'
    elif int(day) <= 91:
        d = str(d - 60) + 'MAR'
    if len(d) == 4:
        d = '0'+str(d)

    month = d[-3:]
    if not os.path.exists('data/inputs/clouds/3DIMG_'+d +
                          '2020_' + time_UTC+'_L2B_CMK_CMK.tif'):
        return



    # input aerosol optical depth from turbidity folder
    gs.run_command('r.in.gdal',
                   input='data/inputs/turbidity/3DIMG_'+d+'2020_' + time_UTC+'_L2G_AOD_AOD.tif',
                   output='aerosol',
                   overwrite=True, flags='o')
    if day in range(1,17):
        cl = 2
    else:
        cl = 0
    # calculating turbidity
    gs.run_command('r.mapcalc.simple',
                   a='aerosol',
                   expression='result = 4.5 + A/0.5 +'+str(cl),
                   output='turbidity',
                   overwrite=True)
    # fill no data cells
    gs.run_command('r.fillnulls',
                   input='turbidity',
                   output='turbidity_filled',
                   method='bilinear',
                   overwrite=True)

    gs.run_command('r.sun',
                   elevation='DEM',
                   horizon_basename='horangle',
                   horizon_step=7.5,
                   aspect='aspect.dem',
                   slope='slope.dem',
                   glob_rad='global_rad',
                   day=day,
                   time=solar_time,
                   nprocs=6,
                   linke='turbidity_filled',
                   albedo_value=0.3,
                   overwrite=True)

    sequence = ['train','valid']
    choice = random.choices(sequence, weights=[4,1])[0]
    if not os.path.exists('data/outputs/0.25@0.25km_'+choice + '/'):
        os.makedirs('data/outputs/0.25@0.25km_'+choice + '/')


    gs.run_command('r.out.gdal',
                   input='global_rad',
                   type='Int16',
                   flags='fc',
                   output='data/outputs/0.25@0.25km_'+choice+'/0.25@0.25km_jamnagar_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True,
                   quiet=True)




# input DEM file
file = 'data/inputs/DEMs/jamnagar_32m_clipped.tif'
# ref_vector = 'data/inputs/vector_mask/full.gpkg'
gs.run_command('r.in.gdal',
               input=file,
               output='DEM',
               overwrite=True)
# gs.run_command('v.in.ogr',
#                input=ref_vector,
#                output='ref_vector',
#                overwrite=True)

# deg: Km
# 0.03455: '4km',
# 0.0086375: '1km',
# 0.002159375: '0.25km',
# 0.0002714 : '0.03km',

res = {
    0.002159375: '0.25km',
}

for res_deg, res_m in res.items():
    gs.run_command('g.region',
                   raster='DEM',
                   rows=208,
                   cols=304)
                    


    counter = 0
    # specify range of day [1-365 int] and time [24h float]
    for day in range(69, 91):
        # 11:30am to 3:30pm IST (6 to 10 UTC)=> about 11 to 3pm solar time
        for time in range(23, 29):
            #if day in {3, 7, 13, 19, 25, 27, 34, 44, 46, 49, 50, 52, 54, 55, 56, 59, 65, 70, 71, 73, 75, 76, 79}: continue
            t = time/2
            counter += 1
            solar_time = t - 0.7 - 0.8792817 + 0.008936339 * \
                day - 0.0001116592*day**2 + 1.586592e-7*day**3
            # solar_time = t  (1.221986 + 0.008938792*day - \
                #   0.0001198693 * day**2 + 2.464719e-7*day**3)/2
            if (day == 69 and t == 12.5) or (day == 70 and t == 12.5): continue
            findSolarInsolation(day, t)

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
import os
from pathlib import Path
import grass.script as gs
from datetime import datetime as d
# change directory because this file is usually imported to grass gis
# os.chdir(os.path.dirname(__file__))  #todo importing not working in linux
# Temperory fix : given absolute path to the this file below and just copy paste the code to grass gis (importing not working in linux)
os.chdir('/home/jyothisable/P.A.R.A/1.Projects/mtp/Softwares/VS code/Solar_Insolation_Calculator')


def findSolarInsolation(day, time):
    '''
    inputs the day and time to find solar insolation for Digital Elevation model present in inputs/DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''
    # assigning region => default boundary and location
    gs.run_command('g.region',
                   #    vector='ref_vector',
                   raster='DEM',
                   res=res_deg)

    # convert time format  # todo use datetime module to do this
    t = int(time*100)-550
    min = str(int(((t % 100)/100)*60))
    if min == '0':
        min = '00'
    time_UTC = '0'+str(t//100) + min if t//100 < 10 else str(t//100) + min

    if day <= 31:
        d = str(day) + 'JAN'
    elif day <= 60:
        d = str(day - 31) + 'FEB'
    elif day <= 91:
        d = str(day - 60) + 'MAR'
    # input cloud data
    gs.run_command('r.in.gdal',
                   input='data/inputs/clouds/3DIMG_'+d+'2020_' + time_UTC+'_L2B_CMK_CMK.tif',
                   output='cloud',
                   overwrite=True, flags='o')
    # cleaning cloud data
    gs.run_command('r.mapcalc.simple',
                   a='cloud',
                   # 0.995 for desert
                   expression='result =(0.965 - A*(A<=1)*0.5)',
                   output='cloud_cf',
                   overwrite=True)

    # calculate solar insolation
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
                   linke_value=linke,
                   albedo_value=0.3,
                   coeff_bh='cloud_cf',
                   overwrite=True)
    # albedo_value=0.3, overwrite=True)

    # os.path.basename(ref_vector).split('.')[0]
    inputFileName = res_m + '_' + 'desert'
    fileNameInGrass = 'global_rad'  # 'global_rad_upscaled'

    '''validate with 4km satelite data => upscale to 4km then take RMS'''
    # input validation data
    gs.run_command('r.in.gdal',
                   input='data/inputs/validation/3DIMG_' +
                   d+'2020_' + time_UTC + '_L2C_INS_INS.tif',
                   output='validation',
                   overwrite=True, flags='o')
    # upscale output radiation to 4km
    gs.run_command('g.region',
                   #    vector='ref_vector',
                   res=0.03455)
    gs.run_command('r.resamp.interp',
                   input='global_rad',
                   output='global_rad_4Km',
                   method='bicubic',
                   overwrite=True)
    # compare using raster calculator
    gs.run_command('r.mapcalc.simple',
                   a='validation',
                   b='global_rad_4Km',
                   expression='result = ((A - B)/A)*((A - B)/A)',
                   output='comp',
                   overwrite=True)
    if counter > 1:
        # add comp_timeAvg raster to current raster
        gs.run_command('r.mapcalc.simple',
                       a='comp',
                       b='comp_timeAvg',
                       expression='result = A + B',
                       output='comp_timeAvg',
                       overwrite=True)
    # copy previous raster to comp_timeAvg
    if counter == 1:
        gs.run_command('g.copy',
                       raster='comp,comp_timeAvg',
                       overwrite=True)

    # output comparison raster
    gs.run_command('r.univar',
                   map='comp',
                   output='data/.cache/stats_cache.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')
    if not os.path.exists('data/outputs/' + res_m + '_validation' + '/'):
        os.makedirs('data/outputs/' + res_m + '_validation' + '/')
    with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/outputs/' + res_m + '_validation' + '/' + res_m + '_validation' + '_stats.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '_validation' + '/' + res_m + '_validation' + '_stats.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    gs.run_command('r.out.gdal',
                   input='comp',
                   output='data/outputs/' + res_m + '_validation' + '/' + res_m + '_validation' +
                   '_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True)
    gs.run_command('r.out.png',
                   input='comp',
                   output='data/outputs/' + res_m + '_validation' + '/' + res_m + '_validation' +
                   '_D'+str(day)+'_H'+str(time)+'.png', compression=0,
                   overwrite=True)
    saveOutput(inputFileName, fileNameInGrass, day, time)


def saveOutput(inputFileName, fileNameInGrass, day, time):
    '''
    input input file name and output file name
    save current output file as .tif in output folder and also append statistics of this file to a .csv file 
    '''
    # output results stats into CSV (can't append directly)
    gs.run_command('r.univar',
                   map=fileNameInGrass,
                   output='data/.cache/stats_cache.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')
    if not os.path.exists('data/outputs/' + res_m + '/'):
        os.makedirs('data/outputs/' + res_m + '/')
    with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/outputs/' + res_m + '/' + inputFileName + '_stats.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '/' + inputFileName + '_stats.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    gs.run_command('r.out.gdal',
                   input=fileNameInGrass,
                   output='data/outputs/' + res_m + '/'+inputFileName +
                   '_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True)
    gs.run_command('r.out.png',
                   input=fileNameInGrass,
                   output='data/outputs/' + res_m + '/'+inputFileName +
                   '_D'+str(day)+'_H'+str(time)+'.png', compression=0,
                   overwrite=True)

    # bicubic interpolation
    # gs.run_command('g.region', raster='global_rad', res=res_deg/4)
    # gs.run_command('r.resamp.interp', input='global_rad',
    #                output='global_rad_upscaled', method='bicubic', overwrite=True)

    # # save interpolation
    # folderpath = 'data/outputs/' + res_m + '_to_' + \
    #     str(float(res_m[:-2])/2) + 'km' + '/'
    # if not os.path.exists(folderpath):
    #     os.makedirs(folderpath)

    # gs.run_command('r.out.gdal',
    #                input='global_rad_upscaled',
    #                output=folderpath + '/' + res_m +
    #                '_to_' + str(float(res_m[:-2])/2) + 'km'
    #                '_D'+str(day)+'_H'+str(time)+'.tif',
    #                overwrite=True)
    # gs.run_command('r.out.png',
    #                input='global_rad_upscaled',
    #                output=folderpath + '/' + res_m +
    #                '_to_' + str(float(res_m[:-2])/2) + 'km'
    #                '_D'+str(day)+'_H'+str(time)+'.png', compression=0,
    #                overwrite=True)


# input DEM file
file = 'data/inputs/DEMs/jamnagar_32m_clipped2.tif'
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
    0.002159375: '0.25km'
}

for res_deg, res_m in res.items():
    gs.run_command('g.region',
                   raster='DEM',
                   #    vector='ref_vector',
                   res=res_deg)

    gs.run_command('r.horizon',
                   elevation='DEM',
                   step=7.5,
                   output='horangle')
    gs.run_command('r.slope.aspect',
                   elevation='DEM',
                   aspect='aspect.dem',
                   slope='slope.dem',
                   overwrite=True)

    # climate data
    solarTimeCorrection = 1.23
    deltaSolar = (1.43 - 1.23)/277
    linke = 7.3
    deltaLinke = (7.3 - 5)/277
    counter = 0

    # specify range of day [1-365 int] and time [24h float]
    for day in range(1, 32):
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        # 11:30am to 3:30pm IST (6 to 10 UTC)=> about 11 to 3pm solar time
        for time in range(23, 32):
            t = time/2
            # skip non existant time (no data from satellite)
            if day == '05' and t == 11.5:
                continue
            elif day == '16' and t == 11.0:
                continue
            elif day == '16' and t == 14.0:
                continue
            counter += 1
            # skip extremely cloudy days
            # if counter in range(41, 64) or counter in range(104, 118) or counter in range(132, 143):
            #     continue

            # finding solar time (only applicable for this location) => need to change #todo find a module to calc this
            solarTimeCorrection += deltaSolar
            solar_time = time/2 - solarTimeCorrection  # 1 for desert 1.23 for jamnagar

            # linke value correction
            linke -= deltaLinke
            findSolarInsolation(day, t)

    # take average of comp_timeAvg with counter
    gs.run_command('r.mapcalc.simple',
                   a='comp_timeAvg',
                   expression='result = sqrt(A/' + str(counter) + ')',
                   output='comp_timeAvg',
                   overwrite=True)
    gs.run_command('r.univar',
                   map='comp_timeAvg',
                   output='data/outputs/' + res_m + '_validation' +
                       '/' + res_m + '_timeAvg_stats.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')
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

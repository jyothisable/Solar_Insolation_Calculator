#!/usr/bin/env python3
# # =============================================================================
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
import grass.script as gs
from datetime import datetime as d
# change directory because this file is usually imported to grass gis
# os.chdir(os.path.dirname(__file__))
os.chdir('/home/jyothisable/P.A.R.A/1.Projects/mtp/Softwares/VS code/Solar_Insolation_Calculator')


def findSolarInsolation(day, time):
    '''
    inputs the day and time to find solar insolation for all the files present in input_DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''
    # convert time format  # todo use time module to do this
    t = int(time*100)-550
    min = str(int(((t % 100)/100)*60))
    if min == '0':
        min = '00'
    time_UTC = '0'+str(t//100) + min if t//100 < 10 else str(t//100) + min
    # input cloud data
    gs.run_command('r.in.gdal',
                   input='data/input_clouds/3DIMG_'+day+'JAN2020_' + time_UTC+'_L2B_CMK_CMK.tif',
                   output='cloud',
                   overwrite=True, flags='o')
    # cleaning cloud data
    gs.run_command('r.mapcalc.simple',
                   a='cloud',
                   expression='result =(1- A*(A<=1)*0.5)',
                   output='cloud_cf',
                   overwrite=True)

    # solar time only applicable for this data set => need to change #todo find a module to calc this
    solar_time = time - 0.75
    # assigning region => default boundary and location
    gs.run_command('g.region',
                   vector='ref_vector',
                   res=res_deg)

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
                   linke_value=7.5,
                   albedo_value=0.3,
                   coeff_bh='cloud_cf',
                   overwrite=True)
    # albedo_value=0.3, overwrite=True)

    inputFileName = res_m + '_' + os.path.basename(ref_vector).split('.')[0]
    fileNameInGrass = 'global_rad'  # 'global_rad_upscaled'
    saveOutput(inputFileName, fileNameInGrass, day, time)


def saveOutput(inputFileName, fileNameInGrass, day, time):
    '''
    input input file name and output file name
    save current output file as .tif in output folder and also append statistics of this file to a .csv file 
    '''
    # output results stats into CSV (can't append directly)
    gs.run_command('r.univar',
                   map=fileNameInGrass,
                   output='data/cache/stats_cache.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')
    if not os.path.exists('data/output/' + res_m + '/'):
        os.makedirs('data/output/' + res_m + '/')
    with open('data/cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/output/' + res_m + '/' + inputFileName + '_stats.csv', 'a') as output_csv:
        if os.stat('data/output/' + res_m + '/' + inputFileName + '_stats.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    gs.run_command('r.out.gdal',
                   input=fileNameInGrass,
                   output='data/output/' + res_m + '/'+inputFileName +
                   '_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True)

    # bicubic interpolation
    gs.run_command('g.region', raster='global_rad', res=res_deg/2)
    gs.run_command('r.resamp.interp', input='global_rad',
                   output='global_rad_upscaled', method='bicubic', overwrite=True)

    # save interpolation
    folderpath = 'data/output/' + res_m + '_to_' + \
        str(float(res_m[:-2])/2) + 'km' + '/'
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)

    gs.run_command('r.out.gdal',
                   input='global_rad_upscaled',
                   output=folderpath + '/' + res_m +
                   '_to_' + str(float(res_m[:-2])/2) + 'km'
                   '_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True)


# input DEM file
file = 'data/input_DEMs/desert_dem_32m_deg.tif'
ref_vector = 'data/input_vector_mask_deg/full.gpkg'
gs.run_command('r.in.gdal',
               input=file,
               output='DEM',
               overwrite=True)
gs.run_command('v.in.ogr',
               input=ref_vector,
               output='ref_vector',
               overwrite=True)

res = {0.03455: '4km',
       0.017275: '2km',
       0.0086375: '1km',
       0.00431875: '0.5km',
       0.002159375: '0.25km'}

for res_deg, res_m in res.items():
    gs.run_command('g.region',
                   vector='ref_vector',
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
    # specify range of day [1-365 int] and time [24h float]
    for day in range(1, 32):
        if day < 10:
            day = '0' + str(day)
        else:
            day = str(day)
        # 11:30am to 3:30pm IST (6 to 10 UTC)=> about 11 to 3pm solar time
        for time in range(23, 32):
            t = time/2
            # skip non existant time
            if day == '05' and t == 11.5:
                continue
            elif day == '16' and t == 11.0:
                continue
            elif day == '16' and t == 14.0:
                continue
            findSolarInsolation(day, t)

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


def findSolarInsolation(day, time):
    '''
    inputs the day and time to find solar insolation for all the files present in input_DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''
    file = 'data/input_DEMs/desert_dem.tif'
    gs.run_command('r.in.gdal', input=file,output='DEM', overwrite=True)
    t = int(time*100)-550
    min = str(int(((t%100)/100)*60))
    if min =='0': min = '00'
    time_UTC = '0'+str(t//100) + min
    # print(time_UTC)
    gs.run_command('r.in.gdal', input='data/input_clouds/3DIMG_'+day+'JAN2020_'+time_UTC+'_L2B_CMK_CMK.tif',output='cloud', overwrite=True, flags='o')
    gs.run_command('r.mapcalc.simple', a='cloud',expression='result = A/3',output='cloud_cf',overwrite=True)
    gs.run_command('r.horizon', elevation='DEM', step=7.5,output='horangle')
    gs.run_command('r.slope.aspect', elevation='DEM',
                    aspect='aspect.dem', slope='slope.dem', overwrite=True)
    # solar time only applicable for this data set => need to change #todo find a module to calc this
    solar_time = time - 0.8
    gs.run_command('r.sun', elevation='DEM', horizon_basename='horangle',
                    horizon_step=7.5, aspect='aspect.dem', slope='slope.dem',
                    glob_rad='global_rad', day=day, time=solar_time, nprocs=6, linke_value=1,
                    albedo_value=0.3,coeff_bh='cloud_cf', overwrite=True)
                    # albedo_value=0.3, overwrite=True)

    res = 0.03618888887999958  # specific to this case 0.0352666666399999
    gs.run_command('r.resamp.interp', input='global_rad',
                    output='global_rad_upscaled', overwrite=True)
    inputFileName = os.path.basename(file).split('.')[0]
    fileNameInGrass = 'global_rad_upscaled'
    saveOutput(inputFileName,fileNameInGrass,day,time)

def saveOutput(inputFileName,fileNameInGrass,day,time):
    '''
    input input file name and output file name
    save current output file as .tif in output folder and also append statistics of this file to a .csv file 
    '''
    # output results stats into CSV (can't append directly)
    gs.run_command('r.univar', map=fileNameInGrass,
                    output='data/cache/stats_cache.csv', separator='comma', overwrite=True, flags='te')
    
    with open('data/cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/output/' + inputFileName + '_stats.csv', 'a') as output_csv:
        if os.stat('data/output/' + inputFileName + '_stats.csv').st_size == 0:
            output_csv.writelines(
                'day,time,non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90')
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

        gs.run_command('r.out.gdal', input=fileNameInGrass,
                       output='data/output/'+inputFileName + '_D'+str(day)+'_H'+str(time)+'.tif', type='Float64', overwrite=True)


# specify range of day [1-365 int] and time [24h float]
for day in range(1, 32):
    if day < 10:day ='0'+ str(day)
    else: day =str(day)
    for time in range(22, 31):  # 11am to 3pm
        t = time/2
        # print('this is day ',day,' and time ',t)
        if day =='05' and t == 11.5: 
            continue 
        elif day =='16' and t== 11.0:
            continue 
        elif day =='16' and t ==14.0: 
            continue 
        findSolarInsolation(day, t)

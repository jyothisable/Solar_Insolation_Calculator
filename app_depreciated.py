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
# change directory because this file is usually imported to grass gis
# os.chdir(os.path.dirname(__file__))  #todo importing not working in linux
# Temperory fix : given absolute path to the this file below and just copy paste the code to grass gis (importing not working in linux)
os.chdir('/home/jyothisable/P.A.R.A/1.Projects/mtp/Softwares/VS code/Solar_Insolation_Calculator')


def findSolarInsolation(day, time):
    '''
    inputs the day and time to find solar insolation for Digital Elevation model present in inputs/DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''

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

    # assigning region => default boundary and location
    gs.run_command('g.region',
                   raster='DEM',
                   res=res_deg)

    # input aerosol optical depth from turbidity folder
    gs.run_command('r.in.gdal',
                   input='data/inputs/turbidity/3DIMG_'+d+'2020_' + time_UTC+'_L2G_AOD_AOD.tif',
                   output='aerosol',
                   overwrite=True, flags='o')
    if day in range(1, 17):
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

    # assigning region => default boundary and location
    gs.run_command('g.region',
                   raster='DEM',
                   vector='ref_vector',
                   res=res_deg)

    # input cloud data
    gs.run_command('r.in.gdal',
                   input='data/inputs/clouds/3DIMG_'+d+'2020_' + time_UTC+'_L2B_CMK_CMK.tif',
                   output='cloud',
                   overwrite=True, flags='o')
    # cleaning cloud data
    gs.run_command('r.mapcalc.simple',
                   a='cloud',
                   # 0.995 for desert
                   expression='result =(1 - A*(A<=1)*0.5)',
                   output='cloud_cf',
                   overwrite=True)

    gs.run_command('r.sun',
                   elevation='DEM',
                   horizon_basename='horangle',
                   horizon_step=1,
                   aspect='aspect.dem',
                   slope='slope.dem',
                   glob_rad='global_rad',
                   day=day,
                   time=solar_time,
                   nprocs=6,
                   linke='turbidity_filled',
                   albedo_value=0.3,
                   coeff_bh='cloud_cf',
                   overwrite=True)

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
    with open('data/outputs/' + res_m + '_validation' + '/' + str(fid)+'_' + res_m + '_validation' + '_stats.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '_validation' + '/' + str(fid)+'_' + res_m + '_validation' + '_stats.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    gs.run_command('r.out.gdal',
                   input='comp',
                   output='data/outputs/' + res_m + '_validation' + '/' + res_m + '_validation' +
                   '_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True)
    # gs.run_command('r.out.png',
    #                input='comp',
    #                output='data/outputs/' + str(fid)+'_' + res_m + '_validation' + '/' + res_m + '_validation' +
    #                '_D'+str(day)+'_H'+str(time)+'.png', compression=0,
    #                overwrite=True)
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
    with open('data/outputs/' + res_m + '/' + str(fid)+'_' + inputFileName + '_stats.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '/' + str(fid)+'_' + inputFileName + '_stats.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    # output validation stats into CSV 
    # gs.run_command('r.univar',
    #                map='validation',
    #                output='data/.cache/stats_cache.csv',
    #                separator='comma',
    #                overwrite=True,
    #                flags='te')

    # with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
    #     lastLine = cache_csv.read().splitlines()[-1]
    # with open('data/outputs/' + res_m + '/' + 'validation_4km_stats.csv', 'a') as output_csv:
    #     if os.stat('data/outputs/' + res_m + '/' + 'validation_4km_stats.csv').st_size == 0:
    #         output_csv.writelines(
    #             "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
    #     output_csv.write("\n")
    #     output_csv.writelines(str(day)+','+str(time)+','+lastLine)
    # output cloud data
    gs.run_command('r.univar',
                   map='cloud_cf',
                   output='data/.cache/stats_cache.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')

    with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/outputs/' + res_m + '/' + str(fid)+'_cloud.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '/' + str(fid) + '_cloud.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    # output turbidity data
    gs.run_command('r.univar',
                   map='turbidity_filled',
                   output='data/.cache/stats_cache.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')

    with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open('data/outputs/' + res_m + '/' + str(fid) + '_turbidity.csv', 'a') as output_csv:
        if os.stat('data/outputs/' + res_m + '/' + str(fid) + '_turbidity.csv').st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

    # output Tiff
    gs.run_command('r.out.gdal',
                   input=fileNameInGrass,
                   output='data/outputs/' + res_m + '/'+inputFileName +
                   '_D'+str(day)+'_H'+str(time)+'.tif',
                   overwrite=True)
    # gs.run_command('r.out.png',
    #                input=fileNameInGrass,
    #                output='data/outputs/' + res_m + '/'+inputFileName +
    #                '_D'+str(day)+'_H'+str(time)+'.png', compression=0,
    #                overwrite=True)

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


# cells
fids = [5, 35, 55, 75, 95, 125, 145, 165, 185, 205, 225, 245, 265]
for fid in fids:

    # input DEM file
    file = 'data/inputs/DEMs/jamnagar_32m_clipped.tif'
    ref_vector = '/home/jyothisable/P.A.R.A/1.Projects/mtp/Dataset/jamnagar/vector_mask/fid_' + \
        str(fid)+'.gpkg'
    gs.run_command('r.in.gdal',
                   input=file,
                   output='DEM',
                   overwrite=True)
    gs.run_command('v.in.ogr',
                   input=ref_vector,
                   output='ref_vector',
                   overwrite=True)

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
                       vector='ref_vector',
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
        for day in range(1, 91):
            # 11:30am to 3:30pm IST (6 to 10 UTC)=> about 11 to 3pm solar time
            for time in range(23, 29):
                t = time/2
                counter += 1
                solar_time = t - 0.7 - 0.8792817 + 0.008936339 * \
                    day - 0.0001116592*day**2 + 1.586592e-7*day**3
                if (day == 69 and t == 12.5) or (day == 70 and t == 12.5):
                    continue
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
                  '/' + str(fid)+'_' + res_m + '_timeAvg_stats.csv', 'a') as output_csv:
            if os.stat('data/outputs/' + res_m + '_validation' +
                       '/' + str(fid)+'_' + res_m + '_timeAvg_stats.csv').st_size == 0:
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

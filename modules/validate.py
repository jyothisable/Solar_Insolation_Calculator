
import os
from modules.outputStats import outputStats
from modules.outputFile import outputFile


def validate(raster, formatedDT, counter):
    '''validate with 4km satelite data => upscale to 4km then take RMS'''
    # input validation data
    gs.run_command('r.in.gdal',
                   input='data/inputs/validation/3DIMG_'+formatedDT+'_L2C_INS_INS.tif',
                   output='validation',
                   overwrite=True, flags='o')

    # upscale output radiation to 4km
    gs.run_command('g.region',
                   res=0.03455)
    gs.run_command('r.resamp.interp',
                   input=raster,
                   output='global_rad_4Km',
                   method='bicubic',
                   overwrite=True)

    # compare and find error raster using raster calculator
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
    elif counter == 1:
        gs.run_command('g.copy',
                       raster='comp,comp_timeAvg',
                       overwrite=True)

    # output comparison raster
    outputCSV_Loc = 'data/outputs/' + res_m + '_validation' + \
        '/' + res_m + '_validation' + '_stats.csv'
    outputRaster = 'comp'
    outputStats(outputCSV_Loc, outputRaster)

    outputFile_Loc = 'data/outputs/' + res_m + '_validation/' + \
        res_m + '_validation' + '_D'+str(day)+'_H'+str(time)+'.tif'

    outputFile(outputFile_Loc, outputRaster)

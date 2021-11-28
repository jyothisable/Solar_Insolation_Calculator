from modules.outputStats import outputStats
from modules.outputFile import outputFile


def RMSPE(sumRaster, counter):
    '''
    find root mean percentage square error using comparison error raster map cleated during validatiion
    '''
    # take average of comp_timeAvg with counter
    gs.run_command('r.mapcalc.simple',
                   a=sumRaster,
                   expression='result = sqrt(A/' + str(counter) + ')',
                   output='rootMeanPE',
                   overwrite=True)

    outputCSV_loc = 'data/outputs/' + res_m + \
        '_validation/' + res_m + '_timeAvg_stats.csv'
    outputFile_loc = 'data/outputs/' + res_m + \
        '_validation/' + res_m + '_timeAvg_validation.tif'
    outputStats(outputCSV_loc, 'rootMeanPE')
    outputFile(outputFile_loc, 'rootMeanPE')

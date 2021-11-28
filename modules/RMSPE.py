from modules.outputStats import outputStats
from modules.outputFile import outputFile


def RMSPE(sumRaster, counter):
    '''
    find root mean square percentage error (RMSPE) using sumRaster raster cleated during validation
    '''
    # take Square root of average of sumRaster with counter
    gs.run_command('r.mapcalc.simple',
                   a=sumRaster,
                   expression='result = sqrt(A/' + str(counter) + ')',
                   output='rootMeanPE',
                   overwrite=True)

    # output stats and raster
    outputCSV_loc = 'data/outputs/' + res_m + \
        '_validation/' + res_m + '_timeAvg_stats.csv'
    outputFile_loc = 'data/outputs/' + res_m + \
        '_validation/' + res_m + '_timeAvg_validation.tif'
    outputStats(outputCSV_loc, 'rootMeanPE')
    outputFile(outputFile_loc, 'rootMeanPE')

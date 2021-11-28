
def RMPE():
    '''
    find root mean percentage square error using comparison error raster map cleated during validatiion
    '''
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

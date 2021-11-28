
import os


def outputStats(outputCSV_Loc, outputRaster):
    '''
    Output statistics of raster file
    '''
    
    # find stats of raster
    gs.run_command('r.univar',
                   map=outputRaster,
                   output='data/.cache/stats_cache.csv',
                   separator='comma',
                   overwrite=True,
                   flags='te')

    # find parent folder of outputCSV_Loc and see if it exists
    outputCSV_FolderLoc = os.path.dirname(outputCSV_Loc)
    if not os.path.exists(outputCSV_FolderLoc):
        os.makedirs(outputCSV_FolderLoc)

    # from cache file, output to csv
    with open('data/.cache/stats_cache.csv', newline='') as cache_csv:
        lastLine = cache_csv.read().splitlines()[-1]
    with open(outputCSV_Loc, 'a') as output_csv:
        if os.stat(outputCSV_Loc).st_size == 0:
            output_csv.writelines(
                "day,time(IST),non_null_cells,null_cells,min,max,range,mean,mean_of_abs,stddev,variance,coeff_var,sum,sum_abs,first_quart,median,third_quart,perc_90")
        output_csv.write("\n")
        output_csv.writelines(str(day)+','+str(time)+','+lastLine)

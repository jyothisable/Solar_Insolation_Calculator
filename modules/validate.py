

def validate(raster)
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

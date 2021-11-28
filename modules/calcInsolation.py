

def findSolarInsolation(day, time, formatedDT):
    '''
    inputs the day and time to find solar insolation for Digital Elevation model present in inputs/DEMs and output
    upscaled version of the insolation data to output folder. stats about this is also available in .csv file
    '''
    # assigning region => default boundary and location
    gs.run_command('g.region',
                   #    vector='ref_vector',
                   raster='DEM',
                   res=res_deg)

    if not os.path.exists('data/inputs/clouds/3DIMG_' + formatedDT + '_L2B_CMK_CMK.tif'):
        return

    # input cloud data
    gs.run_command('r.in.gdal',
                   input='data/inputs/clouds/3DIMG_' + formatedDT + '_L2B_CMK_CMK.tif',
                   output='cloud',
                   overwrite=True, flags='o')
    # cleaning cloud data
    gs.run_command('r.mapcalc.simple',
                   a='cloud',
                   # 0.995 for desert
                   expression='result =(0.965 - A*(A<=1)*0.5)',
                   output='cloud_cf',
                   overwrite=True)

    # input aerosol optical depth from turbidity folder
    gs.run_command('r.in.gdal',
                   input='data/inputs/turbidity/3DIMG_'+d+'2020_' + time_UTC+'_L2G_AOD_AOD.tif',
                   output='aerosol',
                   overwrite=True, flags='o')

    # calculating turbidity
    gs.run_command('r.mapcalc.simple',
                   a='aerosol',
                   expression='result = 1 + A/0.03',
                   output='turbidity',
                   overwrite=True)
    # fill no data cells
    gs.run_command('r.fillnulls',
                   input='turbidity',
                   output='turbidity_filled',
                   method='bicubic',
                   overwrite=True)

    solar_time = time - 1.221986 + 0.008938792*day - \
        0.0001198693 * day**2 + 2.464719e-7*day**3

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

    return 'global_rad'
    # os.path.basename(ref_vector).split('.')[0]
    inputFileName = res_m + '_' + 'desert'
    fileNameInGrass = 'global_rad'  # 'global_rad_upscaled'

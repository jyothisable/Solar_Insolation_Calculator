
def initialize(raster):
    '''
    Input DEM and find horizon, slope and aspect (only need once per location and resolution)
    '''
    gs.run_command('r.in.gdal',
                   input=raster,
                   output='DEM',
                   overwrite=True)
    gs.run_command('g.region',
                   raster='DEM',
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

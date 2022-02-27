#!/home/jyothisable/anaconda3/bin python
print("Hello World")
# # =============================================================================
# Created By  : Athul Jyothis
# Created Date: 18-08-2021 00:17:21
# =============================================================================
"""
The module has been build for calculating and validating the solar insolation of a region using GRASS GIS python API.
Note: To avoid unwanted data loss new statistcis results always append to previous one in CSV files, before running again manually delete or move it.
"""
# user defined modules
from modules.initialize import initialize
from modules.calcInsolation import calcInsolation
from modules import datetime
from modules.validate import validate
from modules.outputFile import outputFile
from modules.outputStats import outputStats
from modules.RMSPE import RMSPE

# inbuilt modules
import os
import grass.script as gs

# change directory because this file is usually imported to grass gis
os.chdir(os.path.dirname(__file__))  # todo importing not working in linux
os.chdir('/home/jyothisable/P.A.R.A/1.Projects/mtp/Softwares/VS code/Solar_Insolation_Calculator')

# Approximate degree to Km convertion reference to use in 'res' dictionary (this depends upon location)
# deg: Km
# 0.03455: '4km',
# 0.0086375: '1km',
# 0.002159375: '0.25km',
# 0.0002714 : '0.03km',

# specify need resolution as {deg: km} key value pair
res = {
    0.0086375: '1km',
    0.0002714: '0.03km',
    0.002159375: '0.25km',
}

# file location of input DEM
DEMfile = 'data/inputs/DEMs/jamnagar_32m_clipped.tif'

for res_deg, res_m in res.items():
    initialize(DEMfile)
    counter = 1
    # specify range of day [1-365 int] and time [24h float]
    for day in range(1, 83):
        # 11:30am to 3:30pm IST (6 to 10 UTC) => about 11 to 3pm solar time
        for time in range(23, 29):
            time = time/2
            formatedDT = datetime.convert(day, time)
            insolation = calcInsolation(formatedDT)
            sumRaster = validate(insolation, formatedDT, counter)
            outputCSV_Loc = 'data/outputs/' + res_m + \
                '/' + res_m + '_' + 'jamnagar' + '_stats.csv'
            outputFile_loc = 'data/outputs/' + res_m + '/' + res_m + '_' + 'jamnagar' +
            '_D'+str(day)+'_H'+str(time)+'.tif'
            outputStats(outputCSV_Loc, insolation)
            outputFile(outputFile_loc, insolation)
            counter += 1
    RMSPE(sumRaster, counter)

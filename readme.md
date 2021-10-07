# Solar Insolation Calculator
This python script uses GRASS GIS software to calculate solar insolation for a given date and time range. The output files are saved in data/output and statistics of output file is also saved in a .csv file in same folder
Note: This script can't run as standalone. GRASS GIS software needs to be installed and then this script can be imported into the software
# How to use
1. Download the whole repo or clone it
2. Place the input DEM (Digital Elevation Model) inside data/inuput_DEMs
3. Change the data and time range if required
4. Open GRASS GIS and import app.py into it and then run it 
5. Result will be available in data/output
6. A CSV file is also created saving the stats of each simulation
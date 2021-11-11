# Solar Insolation Calculator

This python script uses GRASS GIS software to calculate solar insolation for a given location, date and time range. The output files are saved in data/outputs and statistics of output file is also saved in a .csv file in same folder.

## what is Solar Insolation / Irradiance?

The measure of the solar energy that is incident on a specified area over a set period of time.

Not all of the solar energy that reaches the Earth actually reaches the surface of the Earth. Although 1367 W/m2 of sunlight strikes the outer atmosphere, about 30% of it is reflected back into space. There are many factors that help determine how much sunlight actually reaches a given area,
some of them include sun angle, air mass, day length, cloud coverage, and pollution levels.

![insolation](https://useruploads.socratic.org/q8fXA67jQf6ebdl6yEG9_energy_balance.jpg)

## Requirements

- [Grass GIS ](https://grass.osgeo.org/download/) version 7.8 or higher

## How to use

1. Download the whole repo or clone it
2. Place the input DEM (Digital Elevation Model), cloud data and validation data in respective folders in data/inputs folder
3. Change the data and time range in app.py if required
4. Open GRASS GIS and import app.py into it and then run it or copy paste the code into grass gis
5. Result will be available in data/output
6. A CSV file is also created saving the stats of each simulation

To know more about input data see the README.md files in respective folders in data/inputs folder.

# Solar Insolation Calculator

This python script uses GRASS GIS software to calculate solar insolation for a given location, date and time range. The output files are saved in data/outputs and statistics of output file is also saved in a .csv file in same folder.

## what is Solar Insolation / Irradiance?

The measure of the solar energy that is incident on a specified area over a set period of time.

Not all of the solar energy that reaches the Earth actually reaches the surface of the Earth. Although 1367 W/m2 of sunlight strikes the outer atmosphere, about 30% of it is reflected back into space. There are many factors that help determine how much sunlight actually reaches a given area,
some of them include sun angle, air mass, day length, cloud coverage, and pollution levels.

![insolation](https://useruploads.socratic.org/q8fXA67jQf6ebdl6yEG9_energy_balance.jpg)

## Importance

It is important to have values for insolation at certain positions on the Earth as these figures are used to help determine the size and output of solar power systems. Values for insolation can help to determine the expected output for solar panels and to understand where on Earth solar panels would be most effective.

As well, insolation is an important consideration in construction. When constructing a building in a particular climate, it is important to understand what the temperature and insolation will be like to ensure maximum comfort and energy efficient building design.

### why calculate insolation when we can measure from satellite data ?

Solar Insolation from satellite data is not at high resolution (about 4km spatial resolution and 30min temporal resolution), but there is a need to have high resolution insolation data for designing small scale solar power systems.

## Requirements

- [Grass GIS ](https://grass.osgeo.org/download/) version 7.8 or higher
- python 3.6 or higher

## How to use / contribute

1. Download the whole repo / clone / fork
2. Place the input DEM (Digital Elevation Model), cloud data, validation, turbidity data in respective folders in data/inputs folder
3. Change the date and time range and resolution in app.py if required.
4. Open GRASS GIS and create a mapset with [WGS84](https://en.wikipedia.org/wiki/World_Geodetic_System) projection and then import app.py into it and then run it or copy paste the code into grass gis
5. Result will be available in data/output
6. CSV files are also created saving the stats of each simulation

To know more about input data, see the README.md files in respective folders in data/inputs folder.

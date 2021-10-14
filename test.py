#!/usr/bin/env python

# Python script to generate a new GRASS GIS 7 location simply from metadata
# Markus Neteler, 2014, 2020

# ?? LINUX USAGE: First set LIBRARY SEARCH PATH
# export LD_LIBRARY_PATH=$(grass78 --config path)/lib
# python start_grass7_create_new_location_ADVANCED.py

# some predefined variables

# Windows
import grass.script.setup as gsetup
import grass.script as grass
import tempfile
import binascii
import shutil
import subprocess
import sys
import os
grass7path = r'C:\OSGeo4W\apps\grass\grass-7.8.dev'
grass7bin_win = r'C:\OSGeo4W\bin\grass78dev.bat'
# Linux
grass7bin_lin = 'grass78'
# MacOSX
grass7bin_mac = '/Applications/GRASS/GRASS-7.8.app/'
# myepsg = '4326' # latlong
myepsg = '3044'  # ETRS-TM32, http://spatialreference.org/ref/epsg/3044/
#myfile = '/home/neteler/markus_repo/books/kluwerbook/data3rd/lidar/lidar_raleigh_nc_spm.shp'
myfile = '/data/maps/world_natural_earth_250m/europe_north_east.tif'
#myfile = r'C:\Dati\Padergnone\square_p95.tif'

###########

# SOFTWARE
if sys.platform.startswith('linux'):
    # we assume that the GRASS GIS start script is available and in the PATH
    # query GRASS 7 itself for its GISBASE
    grass7bin = grass7bin_lin
elif sys.platform.startswith('win'):
    grass7bin = grass7bin_win
else:
    OSError('Platform not configured.')

startcmd = grass7bin + ' --config path'

p = subprocess.Popen(startcmd, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print >>sys.stderr, 'ERROR: %s' % err
    print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
    sys.exit(-1)
if sys.platform.startswith('linux'):
    gisbase = out.strip('\n')
elif sys.platform.startswith('win'):
    if out.find("OSGEO4W home is") != -1:
        gisbase = out.strip().split('\n')[1]
    else:
        gisbase = out.strip('\n')
    os.environ['GRASS_SH'] = os.path.join(gisbase, 'msys', 'bin', 'sh.exe')

# Set GISBASE environment variable
os.environ['GISBASE'] = gisbase
# define GRASS-Python environment
gpydir = os.path.join(gisbase, "etc", "python")
sys.path.append(gpydir)
########
# define GRASS DATABASE
if sys.platform.startswith('win'):
    gisdb = os.path.join(os.getenv('APPDATA', 'grassdata'))
else:
    gisdb = os.path.join(os.getenv('HOME', 'grassdata'))

# override for now with TEMP dir
gisdb = os.path.join(tempfile.gettempdir(), 'grassdata')
try:
    os.stat(gisdb)
except:
    os.mkdir(gisdb)

# location/mapset: use random names for batch jobs
string_length = 16
location = binascii.hexlify(os.urandom(string_length))
mapset = 'PERMANENT'
location_path = os.path.join(gisdb, location)

# Create new location (we assume that grass7bin is in the PATH)
#  from EPSG code:
startcmd = grass7bin + ' -c epsg:' + myepsg + ' -e ' + location_path
#  from SHAPE or GeoTIFF file
#startcmd = grass7bin + ' -c ' + myfile + ' -e ' + location_path

print startcmd
p = subprocess.Popen(startcmd, shell=True,
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
if p.returncode != 0:
    print >>sys.stderr, 'ERROR: %s' % err
    print >>sys.stderr, 'ERROR: Cannot generate location (%s)' % startcmd
    sys.exit(-1)
else:
    print 'Created location %s' % location_path

# Now the location with PERMANENT mapset exists.

########
# Now we can use PyGRASS or GRASS Scripting library etc. after
# having started the session with gsetup.init() etc

# Set GISDBASE environment variable
os.environ['GISDBASE'] = gisdb

# Linux: Set path to GRASS libs (TODO: NEEDED?)
path = os.getenv('LD_LIBRARY_PATH')
dir = os.path.join(gisbase, 'lib')
if path:
    path = dir + os.pathsep + path
else:
    path = dir
os.environ['LD_LIBRARY_PATH'] = path

# language
os.environ['LANG'] = 'en_US'
os.environ['LOCALE'] = 'C'

# Windows: NEEDED?
#path = os.getenv('PYTHONPATH')
#dirr = os.path.join(gisbase, 'etc', 'python')
# if path:
#    path = dirr + os.pathsep + path
# else:
#    path = dirr
#os.environ['PYTHONPATH'] = path

# print os.environ

# Import GRASS Python bindings

###########
# Launch session and do something
gsetup.init(gisbase, gisdb, location, mapset)

# say hello
grass.message('--- GRASS GIS 7: Current GRASS GIS 7 environment:')
print grass.gisenv()

# do something in GRASS now...

grass.message('--- GRASS GIS 7: Checking projection info:')
in_proj = grass.read_command('g.proj', flags='jf')

# selective proj parameter printing
kv = grass.parse_key_val(in_proj)
print kv
print kv['+proj']

# print full proj parameter printing
in_proj = in_proj.strip()
grass.message("--- Found projection parameters: '%s'" % in_proj)

# show current region:
grass.message('--- GRASS GIS 7: Checking computational region info:')
in_region = grass.region()
grass.message("--- Computational region: '%s'" % in_region)

# do something else: r.mapcalc, v.rectify, ...

# Finally remove the temporary batch location from disk
print 'Removing location %s' % location_path
shutil.rmtree(location_path)

sys.exit(0)

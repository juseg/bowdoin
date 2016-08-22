#!/bin/bash

# make directory or update modification date
mkdir -p external
touch external
cd external

# Measures Greenland ice mapping project (GIMP) dem
orig=ftp://sidads.colorado.edu/pub/DATASETS/nsidc0645_MEASURES_gimp_dem_v1/30/gimpdem0_4.tif
dest=$(basename $orig)
[ -f "$dest" ] || wget $orig

# Greenland Climate Change Initiative (CCI) 2015 velocity map
root=ogive:/scratch_net/ogive/juliens/geodata/icesheets/greenland-cci
orig=$root/greenland_ice_velocity_map_winter_2014_2015/\
greenland_iv_500m_s1_20141101_20151201_v1_0.nc
dest=$(basename $orig)
[ -f "$dest" ] || scp $orig $dest

## Greenland Climate Change Initiative (CCI) 2016 velocity map
#root=ogive:/scratch_net/ogive/juliens/geodata/icesheets/greenland-cci
#orig=$root/greenland_ice_velocity_map_winter_2015_2016/\
#greenland_iv_500m_s1_20151223_20160331_v1_0.nc
#dest=$(basename $orig)
#[ -f "$dest" ] || scp $orig $dest

# Greenland gravimetric mass balance (GMB) grids
orig=ogive:/scratch_net/ogive/juliens/geodata/icesheets/greenland-gmb/GIS_GMB_grid.nc
dest=$(basename $orig)
[ -f "$dest" ] || scp $orig $dest

# Qaanaaq Sentinel-2A (S2A) image from 08 Aug. 2016
orig=ogive:/scratch_net/ogive/juliens/geodata/satellite/sentinel-2a/composite/qaanaaq/rgb/S2A_20160808_175915_456_RGB.jpg
dest=$(basename $orig)
[ -f "$dest" ] || scp $orig ${orig%.jpg}.jpw $dest
[ -f "${dest%.jpg}.jpw" ] || scp ${orig%.jpg}.jpw ${dest%.jpg}.jpw

## Greenland Measures velocity maps
#root=ftp://n5eil01u.ecs.nsidc.org/SAN/MEASURES/NSIDC-0478.001
#for date in 2000.09.03 2005.12.13 2006.12.18 2007.11.01 2008.12.01
#do
#    year=${date:0:4}
#    orig=$root/$date/greenland_vel_mosaic500_$((year))_$((year+1)).tif
#    dest=$(basename $orig)
#    [ -f "$dest" ] || wget $orig
#done

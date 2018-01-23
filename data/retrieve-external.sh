#!/bin/bash

# make directory or update modification date
mkdir -p external
touch external
cd external

## Greenland MEaSUREs Ice Mapping Project (GIMP) dem
#orig=ftp://sidads.colorado.edu/pub/DATASETS/nsidc0645_MEASURES_gimp_dem_v1/30/gimpdem0_4.tif
#dest=$(basename $orig)
#[ -f "$dest" ] || wget $orig

# Greenland MEaSUREs 250m multi-year velocity mosaic
orig=ftp://sidads.colorado.edu/DATASETS/nsidc0670_MEASURES_my_vel_mosaic_v1/\
greenland_vel_mosaic250_v1.tif
dest=$(basename $orig)
[ -f "$dest" ] || wget $orig

## Greenland Climate Change Initiative (CCI) 2015 velocity map
#root=ogive:/scratch_net/ogive/juliens/geodata/icesheets/greenland-cci
#orig=$root/greenland_ice_velocity_map_winter_2014_2015/\
#greenland_iv_500m_s1_20141101_20151201_v1_0.nc
#dest=$(basename $orig)
#[ -f "$dest" ] || scp $orig $dest

## Greenland Climate Change Initiative (CCI) 2016 velocity map
#root=ogive:/scratch_net/ogive/juliens/geodata/icesheets/greenland-cci
#orig=$root/greenland_ice_velocity_map_winter_2015_2016/\
#greenland_iv_500m_s1_20151223_20160331_v1_0.nc
#dest=$(basename $orig)
#[ -f "$dest" ] || scp $orig $dest

# Global Sea Level Observing System (GLOSS) Pituffik tide data
orig="http://ilikai.soest.hawaii.edu/woce/h808.dat"
dest=$(basename $orig)
[ -f "$dest" ] || wget $orig -o $dest

# Office desktop locations
geodata="iceberg:/scratch_net/iceberg_second/juliens/geodata"
s2adata="$geodata/satellite/sentinel-2a"

# Greenland gravimetric mass balance (GMB) grids
orig=$geodata/icesheets/greenland-gmb/GIS_GMB_grid.nc
dest=$(basename $orig)
[ -f "$dest" ] || scp $orig $dest

# Yvo's DEM
orig="iceberg:/usr/itetnas01/data-vaw-01/glazioarch/GlacioProject/bowdoin/\
bowdoin_2015/GIS/Data/DSM/bowdoin_20100904_15m_20140929.tif"
dest="$(basename $orig)"
[ -f "$dest" ] || scp $orig $dest

# Qaanaaq Sentinel-2A (S2A) images
for date in 20160410_180125_659 20160808_175915_456
do
    orig=$s2adata/composite/greenland/qaanaaq/rgb/S2A_${date}_RGB.jpg
    dest=$(basename $orig)
    [ -f "$dest" ] ||[ -f "${dest%.jpg}.jpw" ] || scp $orig ${orig%.jpg}.jpw .
done

#!/bin/sh

# make directory or update modification date
mkdir -p external
touch external
cd external

# measures gimp dem
url=ftp://sidads.colorado.edu/pub/DATASETS/nsidc0645_MEASURES_gimp_dem_v1/30/gimpdem0_4.tif
fname=${url##*/}
[ -f $fname ] || wget $url

# measures velocities
root=ftp://n5eil01u.ecs.nsidc.org/SAN/MEASURES/NSIDC-0478.001
for date in 2000.09.03 2005.12.13 2006.12.18 2007.11.01 2008.12.01
do
    year=${date:0:4}
    url=$root/$date/greenland_vel_mosaic500_$((year))_$((year+1)).tif
    fname=${url##*/}
    [ -f $fname ] || wget $url
done
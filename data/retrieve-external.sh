#!/bin/bash

# make directory or update modification date
mkdir -p external
touch external
cd external

# Arctic DEM crop on Bowdoin
# (for UTM 19 use -t_srs EPSG:32619 -te 500000 8615000 520000 8630000)
# (two more strips contain data over Bowdoin:
#  * SETSM_WV02_20120512_103001001932B700_1030010018CB9600_seg1_2m_v2.0, and
#  * SETSM_WV02_20140906_103001003766BC00_1030010036B2F000_seg4_2m_v2.0)
root=http://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/geocell/v2.0/n77w069/
for strp in SETSM_WV01_20120730_102001001C3CA200_102001001C997D00_seg3_2m_v2.0 \
            SETSM_WV02_20130404_1030010020AC5E00_1030010021347000_seg1_2m_v2.0 \
            SETSM_WV01_20140906_10200100318E9F00_1020010033454500_seg2_2m_v2.0
do
    if [ ! -f "${strp}.tif" ]
    then
        wget -nc $root/$strp.tar
        tar -kxf $strp.tar
        gdalwarp -r cubic -te -540000 -1230000 -530000 -1220000 \
            ${strp}_dem.tif ${strp}.tif
    fi
done

## Greenland MEaSUREs Ice Mapping Project (GIMP) dem
#orig=ftp://sidads.colorado.edu/pub/DATASETS/nsidc0645_MEASURES_gimp_dem_v1/30/gimpdem0_4.tif
#dest=$(basename $orig)
#[ -f "$dest" ] || wget $orig

# Greenland MEaSUREs 250m multi-year velocity mosaic
# FIXME update to Greenland CCI
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
[ -f "$dest" ] || wget $orig

# Intergovernmental Oceanographic Commission (IOC) Pituffik tide data
for date in 2014{07..12} 20{15..16}{01..12} 2017{01..07}
do
    nexy="$((${date:0:4}+10#${date:4:2}/12))"  # year of next month
    nexm="$(printf "%02d" $((10#${date:4:2}%12+01)))"  # next month
    root="http://www.ioc-sealevelmonitoring.org/bgraph.php"
    args="code=thul&output=tab&period=30&endtime=$nexy-$nexm-01"
    orig="$root?$args"
    dest="tide-thul-$date.csv"
    [ -f "$dest" ] || wget $orig -O - | sed -e "s:</th>:\n:g" \
                                            -e "s:</td></tr>:\n:g" \
                                            -e "s:</td>:,:g" \
                                            -e "s:<[^>]*>::g" > $dest
done

# SIGMA-B automatic weather station data
for year in 20{14..17}
do
    serv="https://mri-2.mri-jma.go.jp/owncloud/index.php"
    root="$serv/s/60a7ce6376755287e4ec6a7eb4d5a839/download?path=%2F&files="
    dest="SIGMA_AWS_SiteB_${year}_level0_final.xls"
    orig="$root$dest"
    [ -f "$dest" ] || wget $orig -O $dest
done

# Office desktop locations
geodata="iceberg:/scratch_net/iceberg_second/juliens/geodata"
s2adata="$geodata/satellite/sentinel-2a"

# Greenland gravimetric mass balance (GMB) grids
orig=$geodata/icesheets/greenland-gmb/GIS_GMB_grid.nc
dest=$(basename $orig)
[ -f "$dest" ] || scp $orig $dest

# Yvo's DEM
# FIXME update to Arctic DEM
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

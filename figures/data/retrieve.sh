#!/bin/bash

# Yvo's DEM
orig="ogive:/usr/itetnas01/data-vaw-01/glazioarch/GlacioProject/bowdoin/\
bowdoin_2015/GIS/Data/DSM/bowdoin_20100904_15m_20140929.tif"
dest="$(basename $orig)"
[ -f "$dest" ] || scp $orig $dest

# Qaanaaq Sentinel-2A (S2A) image from 08 Aug. 2016
orig=ogive:/scratch_net/ogive_second/juliens/geodata/satellite/sentinel-2a/\
composite/greenland/qaanaaq/rgb/S2A_20160410_180125_659_RGB.jpg
dest=$(basename $orig)
[ -f "$dest" ] || scp $orig ${orig%.jpg}.jpw .
[ -f "${dest%.jpg}.jpw" ] || scp ${orig%.jpg}.jpw ${dest%.jpg}.jpw

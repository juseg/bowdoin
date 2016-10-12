#!/bin/bash

# Yvo's DEM
orig="ogive:/usr/itetnas01/data-vaw-01/glazioarch/GlacioProject/bowdoin/\
bowdoin_2015/GIS/Data/DSM/bowdoin_20100904_15m_20140929.tif"
dest="$(basename $orig)"
[ -f "$dest" ] || scp $orig $dest

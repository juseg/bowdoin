#!/bin/bash
# Copyright (c) 2016-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# make directory or update modification date
mkdir -p external
touch external
cd external


# Bowdoin temperature paper data
# ------------------------------

# Arctic v3.0 DEM crop on Bowdoin (manual selection from 24 Sep 2025 using the
# online shapefile and bowtem_demseries figure script to find strips with more
# coverage and fewer artefacts; for transformation to UTM 19 coordinate append
# -t_srs EPSG:32619 -te 500000 8615000 520000 8630000 to gdalwarp command).
root="https://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/strips/latest/2m/n77w069"
for strp in \
    SETSM_s2s041_WV01_20120730_102001001C3CA200_102001001C997D00_2m_lsf_seg2 \
    SETSM_s2s041_WV02_20130404_1030010020AC5E00_1030010021347000_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20140906_10200100318E9F00_1020010033454500_2m_lsf_seg2 \
    SETSM_s2s041_WV02_20140906_103001003766BC00_1030010036B2F000_2m_lsf_seg2 \
    SETSM_s2s041_WV02_20150419_10300100403C2300_1030010041149700_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20160424_10300100566BCD00_103001005682C900_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20160504_10300100557E8400_1030010055147100_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20170318_10200100602AB700_102001005FDC9000_2m_lsf_seg1 \
    SETSM_s2s041_WV03_20180424_104001003C59FD00_104001003C25E800_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20180502_10200100747CC100_10200100765FE000_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20200318_10300100A3C33B00_10300100A5617100_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20200410_10300100A31A0600_10300100A36D6500_2m_lsf_seg1 \
    SETSM_s2s041_W1W1_20200606_10200100965E3000_102001009A43F300_2m_lsf_seg5 \
    SETSM_s2s041_WV03_20201002_1040010060C03000_1040010061634200_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20210501_10300100BD76C300_10300100BE22CD00_2m_lsf_seg1 \
    SETSM_s2s041_W1W1_20210922_10200100B6DF1C00_10200100B787C400_2m_seg2 \
    SETSM_s2s041_WV01_20220418_10200100C1DA0E00_10200100C4A08100_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20230626_10200100DAA77300_10200100DBCCB300_2m_seg1 \
    SETSM_s2s041_WV01_20240701_10200100F18B1E00_10200100F1AFEA00_2m_seg1 \
    SETSM_s2s041_WV03_20240706_10400100989EFC00_1040010098D1C000_2m_seg1
do
    if [ ! -f "${strp}.tif" ]
    then
        wget -nc $root/$strp.tar.gz
        tar -kxf $strp.tar.gz ${strp}_dem.tif
        gdalwarp -r cubic -te -540000 -1230000 -530000 -1220000 \
            ${strp}_dem.tif ${strp}.tif
        rm $strp.tar.gz ${strp}_dem.tif
    fi
done


# Bowdoin pressure paper data
# ---------------------------

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

# Bowdoin deformation paper data
# ------------------------------

# SIGMA-B automatic weather station data
for year in 20{14..17}
do
    serv="https://mri-2.mri-jma.go.jp/owncloud/index.php"
    root="$serv/s/60a7ce6376755287e4ec6a7eb4d5a839/download?path=%2F&files="
    dest="SIGMA_AWS_SiteB_${year}_level0_final.xls"
    orig="$root$dest"
    [ -f "$dest" ] || wget $orig -O $dest
done

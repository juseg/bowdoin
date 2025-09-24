#!/bin/bash

# make directory or update modification date
mkdir -p external
touch external
cd external


# Bowdoin temperature paper data
# ------------------------------

# Arctic v3.0 DEM crop on Bowdoin
# (strips manually selected through index shapefile available online)
# (for UTM 19 use -t_srs EPSG:32619 -te 500000 8615000 520000 8630000)
root="https://data.pgc.umn.edu/elev/dem/setsm/ArcticDEM/strips/latest/2m/n77w069"
for strp in \
    SETSM_s2s041_W1W1_20150427_102001003C04A300_102001003ECD7100_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20170318_10200100602AB700_102001005FDC9000_2m_lsf_seg1 \
    SETSM_s2s041_W1W2_20150425_102001003DA28D00_10300100419E5700_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20120730_102001001C3CA200_102001001C997D00_2m_lsf_seg2 \
    SETSM_s2s041_W2W2_20150530_10300100421BB000_103001004254F700_2m_lsf_seg1 \
    SETSM_s2s041_WV01_20170318_10200100602AB700_102001005FDC9000_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20130404_1030010020AC5E00_1030010021347000_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20140906_103001003766BC00_1030010036B2F000_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20150419_10300100403C2300_1030010041149700_2m_lsf_seg1 \
    SETSM_s2s041_WV02_20160504_10300100557E8400_1030010055147100_2m_lsf_seg1 \
# (strip used in bowtem paper, but as of 20220719 error 302 moved temporarily)
#           SETSM_W1W2_20140905_10200100318E9F00_1030010037BBC200_seg3_2m_v3.0 \
# (as of 20250922 the following strips are missing but check root url for more)
#     SETSM_s2s041_W2W2_20150530_10300100421BB000_103001004254F700_2m_lsf_seg2 \
#     SETSM_s2s041_W2W2_20150530_10300100421BB000_103001004254F700_2m_lsf_seg3 \
#     SETSM_s2s041_WV01_20140906_10200100318E9F00_1020010033454500_2m_lsf_seg4 \
#     SETSM_s2s041_WV02_20120512_103001001932B700_1030010018CB9600_2m_lsf_seg6 \
#     SETSM_s2s041_WV02_20160424_10300100566BCD00_103001005682C900_2m_lsf_seg6 \
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

# Greenland MEaSUREs 100m ice velocity for selected sites
server=https://daacdata.apps.nsidc.org/pub/DATASETS/
dataset=nsidc0646_MEASURES_greenland_vel_optical_v2/Wcoast-77.80N/
if [ "$(find OPT_W77.80N_*.tif | wc -l)" != 40 ]
then
    wget \
        --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies \
        --keep-session-cookies --no-check-certificate --auth-no-challenge=on \
        --recursive --no-directories --no-parent --execute robots=off \
        --accept 'OPT_W77.80N_201[4-7]*_v?_v2.tif' \
        $server/$dataset
fi

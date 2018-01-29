#!/bin/bash

# host containing original files
host="iceberg"

# animation name and paths
outname="anim_bowdoin_s2a"
basedir="/scratch_net/iceberg_second/juliens/geodata/satellite/sentinel-2a"
tempdir="/scratch_net/iceberg/juliens/anim/$outname"

# list of dates picked for animation
datelist="
20160318_175038_458
20160321_180021_460
20160324_181004_462
20160325_174028_749
20160327_181959_462
20160328_175044_578
20160403_180957_459
20160406_181959_460
20160407_174950_459
20160410_180125_659
20160414_173948_462
20160417_174954_463
20160424_174125_261
20160504_173947_147
20160506_181935_287
20160503_180920_455
20160504_173947_147
20160506_181935_287
20160507_174912_457
20160517_174913_462
20160523_180922_457
20160524_173944_536
20160605_181924_458
20160615_181922_460
20160618_182919_461
20160628_182918_458
20160706_174910_456
20160708_182920_459
20160712_180919_461
20160713_174015_006
20160715_181924_456
20160723_173907_455
20160729_175916_460
20160730_172902_461
20160808_175915_456
20160809_172902_463
20160815_174910_462
20160910_181050_650
20160913_181945_463
20160918_172958_464
20160923_182055_459
"

# cloud-free dates not picked
unselect="
20160322_173001_458  # slight overcast
20160421_172942_462  # small clouds
20160509_182933_282  # se corner cut
20160516_181926_455  # slight overcase
20160521_172904_459  # small clouds
20160529_182922_461  # small clouds
20160612_180919_456  # small clouds
20160626_174908_464  # small clouds
20160722_181050_652  # small clouds
20160825_174913_066  # overcast
20160829_172859_459  # large clouds
20160917_180022_497  # small clouds
"

# create local frame directory if needed
mkdir -p $outname

# prepare individual frames and save a local copy
i=0
ssh $host mkdir -p $tempdir
for date in $datelist
do
    ifile="$basedir/composite/greenland/qaanaaq/rgb/S2A_${date}_RGB.jpg"
    ofile="$tempdir/$(printf "%04d" $i).png"
    label="$(date -d${date:0:8} -u -R | cut -d ' ' -f 2-4)"
    if [ ! -f $outname/$(basename $ofile) ]
    then
        ssh $host "convert \
-gravity northwest -crop 2400x1600+3200+2800 -resize 1800x1200 +repage \
-gravity northeast -annotate +25+25 \"$label\" -pointsize 24 -fill black \
-font DejaVu-Sans-Bold $ifile $ofile"
        scp $host:$ofile $outname
    fi
    i=$((i+1))
done

## assemble gif animation
#convert -delay 20 -loop 0 $outname/????.png -layers Optimize $outname.gif

# assemble video animation
options="-r 5 -i $outname/%04d.png -pix_fmt yuv420p"
avconv $options -c:v libx264 $outname.mp4 -y
avconv $options -c:v theora $outname.ogg -y

# remove local frames
# rm -r frames

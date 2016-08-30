#!/bin/bash

# host containing original files
host="ogive"

# animation name and paths
outname="anim_bowdoin_s2a"
basedir="/scratch_net/ogive/juliens/geodata/satellite/sentinel-2a"
tempdir="/scratch_net/ogive/juliens/anim/$outname"

# list of dates picked for animation
datelist="
20160504_173947_147
20160507_174912_457
20160509_182933_282
20160517_174913_462
20160521_172904_459
20160524_173944_536
20160612_180919_456
20160615_181922_460
20160618_182919_461
20160626_174908_464
20160628_182918_458
20160706_174910_456
20160708_182920_459
20160712_180919_461
20160713_174015_006
20160715_181924_456
20160723_173907_455
20160730_172902_461"

# cloud-free dates not picked
#20160503_180920_455
#20160506_181935_287
#20160516_181926_455
#20160523_180922_457
#20160529_182922_461

# create local frame directory if needed
mkdir -p $outname

# prepare individual frames and save a local copy
i=0
ssh $host mkdir -p $tempdir
for date in $datelist
do
    ifile="$basedir/composite/qaanaaq/rgb/S2A_${date}_RGB.tif"
    ofile="$tempdir/$(printf "%04d" $i).png"
    label="$(date -d${date:0:8} -u -R | cut -d ' ' -f 2-4)"
    if [ ! -f $outname/$(basename $ofile) ]
    then
        ssh $host "convert -quiet \
-crop 1200x1600+3800+2800 +repage -resize 50% \
-gamma 5.05,5.10,4.85 -sigmoidal-contrast 15,50% -modulate 100,150 \
-unsharp 0x1 -annotate +24+48 \"$label\" -pointsize 24 -fill black \
$ifile $ofile"
        scp $host:$ofile $outname
    fi
    i=$((i+1))
done

# assemble gif animation
convert -delay 20 -loop 0 $outname/????.png -layers Optimize $outname.gif

# assemble video animation
options="-r 5 -i $outname/%04d.png -pix_fmt yuv420p"
ffmpeg $options -c:v libx264 $outname.mp4 -y
ffmpeg $options -c:v theora $outname.ogg -y

# remove local frames
# rm -r frames

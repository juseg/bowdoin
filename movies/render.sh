#!/bin/bash
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

# Add bumper frames and fading effects to any animation

# command-line arguments
prefix="${1:-anim}"
subtitle="${2:-none}"

# look for input file(s)
[ -f ${prefix}_main.mp4 ] && iargs="-i ${prefix}_main.mp4" ||
    iargs="-pattern_type glob -i $HOME/anim/$prefix/{??????}.png"

# get input stream height
height=$(ffprobe -v error -show_entries stream=height -of csv=p=0 $iargs)

# prepare bumper frames
python stills.py $prefix.yaml --subtitle $subtitle --height=$height

# assembling parametres
fade=12  # number of frames for fade in and fade out effects
hold=25  # number of frames to hold in the beginning and end
secs=$((120+2*hold/25))  # duration of main scene in seconds

# prepare filtergraph for main scene
filt="[0]tpad=$hold:$hold:clone:clone"   # clone first and last frames

# add title frame and bumpers
filt+=",fade=in:0:$fade,fade=out:$((secs*25-fade)):$fade[main];"  # main scene
filt+="[1]fade=in:0:$fade,fade=out:$((4*25-fade)):$fade[head];"  # title frame
filt+="[2]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[refs];"  # references
filt+="[3]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[disc];"  # disclaimer
filt+="[4]fade=in:0:$fade,fade=out:$((3*25-fade)):$fade[bysa];"  # license
filt+="[head][main][refs][disc][bysa]concat=5"

# assemble video
ffmpeg $iargs \
    -loop 1 -t 4 -i ${prefix}_head.png \
    -loop 1 -t 3 -i ${prefix}_refs.png \
    -loop 1 -t 3 -i ${prefix}_disc.png \
    -loop 1 -t 3 -i ${prefix}_bysa.png \
    -filter_complex $filt -pix_fmt yuv420p -c:v libx264 -r 25 \
    ${prefix}.mp4

# accelerate for social media (always 2k resolution)
ffmpeg \
    -i ${prefix}.mp4 -s 1920x1080 -vf "trim=5:125,setpts=PTS/10" \
    ${prefix}_x10.mp4

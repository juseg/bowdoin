#!/bin/sh
#
# Script used to extract PNG images from Conny's design PDFs

# extract images somehow cut into small strips
pdfimages -all Gehäuse_50-210mm_05_A4{.pdf,}
pdfimages -all Gehäuse_50-210mm_06{.pdf,}

# patch matching strips into complete images
options="-append -trim -gravity center -extent"
prefix="diboss_view"
magick Gehäuse_50-210mm_05_A4-0{03..02}.png ${options} 3000x600 ${prefix}_01.png
magick Gehäuse_50-210mm_06-0{03..00}.png ${options} 600x2600 ${prefix}_02.png
magick Gehäuse_50-210mm_06-0{19..06}.png ${options} 4200x2400 ${prefix}_03.png
magick Gehäuse_50-210mm_06-0{24..22}.png ${options} 800x1200 ${prefix}_04.png
magick Gehäuse_50-210mm_06-0{31..28}.png ${options} 5800x800 ${prefix}_05.png

# remove image strips
gio trash Gehäuse_50-210mm_*.png

# keep dimensions as pdf
cp Gehäuse_50-210mm_07.pdf diboss_dims.pdf

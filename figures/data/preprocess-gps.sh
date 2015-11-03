#!/bin/bash

readme="original/gps/readme_B14BH1.txt"
ifile="original/gps/B14BH1_20??_15min.dat"
ofile="processed/bowdoin-gps-upstream.csv"

# grep header line, remove (units) and convert spaces to commas
grep latitude $readme | sed -e "s/([a-Z ]*)//g" -e "s| [ ]*|,|g" -e "s|GPST|date|" > $ofile

# concatenate two input files, reformat dates and spaces to commas
cat $ifile | sed -e "s|/|-|g" -e "s|  [ ]*|,|g" -e "s:.00[01]::" >> $ofile

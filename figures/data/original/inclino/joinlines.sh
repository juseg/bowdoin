#!/bin/bash
# Join broken lines on data files retrieved from memory cars to match them with
# data files retrieved directly from data loggers.

inputfile=$1

cat $inputfile \
    | tr '\n' ';' \
    | sed -e 's/\r;","/  ","/g' -e 's/\r;"\r;/  "\r;/g' \
    | tr ';' '\n'

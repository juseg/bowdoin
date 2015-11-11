#!/usr/bin/env python2

import numpy as np
import pandas as pd

columns = ['daydate', 'time', 'lat', 'lon', 'z', 'Q', 'ns',
           'sdn', 'sde', 'sdu', 'sdne', 'sdeu', 'sdun', 'age', 'ratio']

# input and output file names
ifilename = 'original/gps/B14BH1_%d_15min.dat'
ofilename = 'processed/bowdoin-gps-upstream.csv'

# read original files
dflist = []
for year in [2014, 2015]:
    dflist.append(
        pd.read_fwf(ifilename % year, names=columns, usecols=columns[0:5],
                    index_col=0, parse_dates={'date': ['daydate', 'time']}))
df = pd.concat(dflist)
df = df[['lon', 'lat', 'z']]

# write csv file
df.to_csv(ofilename)


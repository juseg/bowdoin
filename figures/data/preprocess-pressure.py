#!/usr/bin/env python2

import datetime
import pandas as pd

# column names
colnames = ['label', 'year', 'day', 'time', 'temp', 'pres', 'wlev']


# date converter
def date_parser(year, day, time):
    datestring = '%04d.%03d.%04d' % tuple(map(int, [year, day, time]))
    return datetime.datetime.strptime(datestring, '%Y.%j.%H%M')

# for each borehole
sensors = ['073303', '094419']
for bh in [1, 2]:
    sensor = sensors[bh-1]

    # input and output file names
    ifilename = 'original/pressure/drucksens%s_final_storage_1.dat' % sensor
    ofilename = 'processed/bowdoin-pressure-bh%d.txt' % bh

    # read original file
    df = pd.read_csv(ifilename, names=colnames,
                     parse_dates={'date': ['year', 'day', 'time']},
                     date_parser=date_parser, index_col='date')

    # write csv file without label column
    df.drop('label', axis=1).to_csv(ofilename)

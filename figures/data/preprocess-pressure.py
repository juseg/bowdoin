#!/usr/bin/env python2

import datetime
import pandas as pd

loggers = {'downstream': 'drucksens073303',
           'upstream':   'drucksens094419'}
columns = ['label', 'year', 'day', 'time', 'temp', 'pres', 'wlev']


# date converter
def date_parser(year, day, time):
    datestring = '%04d.%03d.%04d' % tuple(map(int, [year, day, time]))
    return datetime.datetime.strptime(datestring, '%Y.%j.%H%M')

# for each borehole
for bh, log in loggers.iteritems():

    # input and output file names
    ifilename = 'original/pressure/%s_final_storage_1.dat' % log
    ofilename = 'processed/bowdoin-pressure-%s.csv' % bh

    # read original file
    df = pd.read_csv(ifilename, names=columns,
                     parse_dates={'date': ['year', 'day', 'time']},
                     date_parser=date_parser, index_col='date')

    # write csv file without label column
    df.drop('label', axis=1).to_csv(ofilename)

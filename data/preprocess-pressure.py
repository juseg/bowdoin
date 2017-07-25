#!/usr/bin/env python2

import datetime
import numpy as np
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

    # read original file
    df = pd.read_csv('original/pressure/%s_final_storage_1.dat' % log,
                     names=columns, index_col='date', date_parser=date_parser,
                     parse_dates={'date': ['year', 'day', 'time']})

    # replace extreme values by nan (including a strange peak on 2017-07-03)
    df[df<-1000.0] = np.nan

    # write csv files
    for var in ['temp', 'wlev']:
        df[var].to_csv('processed/bowdoin-pressure-%s-%s.csv' % (var, bh),
                       header=True)

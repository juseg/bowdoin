#!/usr/bin/env python2

import datetime
import numpy as np
import pandas as pd

loggers = {'lower': 'drucksens073303',
           'upper': 'drucksens094419'}
columns = ['label', 'year', 'day', 'time', 'temp', 'pres', 'wlev']


def date_parser(year, day, time):
    datestring = '%04d.%03d.%04d' % tuple(map(int, [year, day, time]))
    return datetime.datetime.strptime(datestring, '%Y.%j.%H%M')


def get_data(bh, log):
    """Return data values in a data frame."""

    # read original file
    df = pd.read_csv('original/pressure/%s_final_storage_1.dat' % log,
                     names=columns, index_col='date', date_parser=date_parser,
                     parse_dates={'date': ['year', 'day', 'time']})

    # replace extreme values by nan (including a strange peak on 2017-07-03)
    df[df<-1000.0] = np.nan

    # return dataframe
    return df


# for each borehole
for bh, log in loggers.iteritems():

    # get all data
    df = get_data(bh, log)

    # extract water level
    wlev = df['wlev'].rename(bh[0].upper() + 'P')
    wlev.to_csv('processed/bowdoin-pressure-wlev-%s.csv' % bh, header=True)

    # extract temperature
    temp = df['temp'].rename(bh[0].upper() + 'P')
    temp.to_csv('processed/bowdoin-pressure-temp-%s.csv' % bh, header=True)

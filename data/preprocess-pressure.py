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


def extract_depth(wlev):
    """Return pressure sensor depths."""

    # observed water depths
    if bh == 'lower':
        observ_date = '2014-07-23 00:30:00'  # assumed
        water_depth = 0.0
    if bh == 'upper':
        observ_date = '2014-07-17 18:07:00'  # assumed
        water_depth = 46.0  # 46 m in pressure borehole, 48 m in tilt

    # compute sensor depth
    depth = wlev.loc[observ_date].mean() + water_depth

    # return as a dataframe
    depth = pd.Series(name=wlev.name, index=[observ_date], data=[depth])
    depth.index = depth.index.rename('date')
    return depth


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

    # extract depths
    depth = extract_depth(wlev)
    depth.to_csv('processed/bowdoin-pressure-depth-%s.csv' % bh, header=True)

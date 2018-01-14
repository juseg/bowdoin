#!/usr/bin/env python2

import numpy as np
import pandas as pd
import util as ut

loggers = {'lower': 'Th-Bowdoin-1',
           'upper':   'Th-Bowdoin-2'}
columns = ['temp%02d' % (i+1) for i in range(16)]


def get_temperature(log, manual=False):
    """Return calibrated temperature in a data frame."""

    # input file names
    postfix = 'Manual' if manual else 'Therm'
    cfilename = 'original/temperature/%s_Coefs.dat' % log
    ifilename = 'original/temperature/%s_%s.dat' % (log, postfix)

    # read rearranged calibration coefficients
    # sensor order lower: BH2A[1-9] + BH2B[1-7],
    #              upper: BH1A[1-9] + BH1B[1-4,7,5-6].
    a1, a2, a3 = np.loadtxt(cfilename, unpack=True)

    # read resistance data
    skiprows = [0] if manual else [0, 2, 3]
    df = pd.read_csv(ifilename, skiprows=skiprows, comment='#',
                     na_values='NAN', index_col=0)
    df = df[['Resist({:d})'.format(i+1) for i in range(16)]]

    # compute temperature from resistance
    df = np.log(df)
    df = 1 / (a1 + a2*df + a3*df**3) - 273.15

    # rename index and columns
    df.index = df.index.rename('date')
    df.columns = columns

    # return as dataframe
    return df


def get_depth(bh):
    """Return temperature sensor depths in a data series."""

    # Measured surfacing cable lenghts
    # * Th-Bowdoin-2: BH1A 2015-07-18 12:30, 19.70 m to 275 m mark
    #   (upper)            2016-07-19 11:45, 21.60 m to 275 m mark
    #                 BH1B 2015-07-18 12:30, 13.40 m to sensor 7
    #                      2016-07-19 11:45, 15.30 m to sensor 7
    #
    # * Th-Bowdoin-1: BH2A 2015-07-18 14:30, 7.30 m to 250 m mark
    #   (lower)            2016-07-19 13:20, 9.70 m to 250 m mark
    #                 BH2B 2015-07-18 14:30, 11.25 m to sensor 6
    #                      2016-07-19 13:20, 13.65 m to sensor 6

    # calculate sensor depths
    if bh == 'lower':
        date = '2015-07-18 14:30'
        bottom = 7.30 - 250.0
        top =  11.25 + 20.0
        lower = bottom + 20.0*np.arange(9)
        upper = top + 20.0*np.arange(-6, 1)
        gap = upper[0] - lower[-1]
        lower += gap - 20.0 # according to conny
    if bh == 'upper':
        date = '2015-07-18 12:30'
        bottom = 19.70 - 275.0
        top =  13.40 + 0.0
        lower = bottom + 20.0*np.arange(9)
        upper = top + 20.0*np.array([-6, -5, -4, -3, 0, -2, -1])

    # lower depths make no sense; mark as unknown
    lower[:] = np.nan
    depth = -np.hstack([lower, upper])

    # except for the lowest sensor, assumed to be at the base
    # ``SMB was measured [...] on Bowdoin Glacier at [...] BH1 (71 m a.s.l.)
    # from 19 July 2014 to 16 July 2015 [...] SMB on Bowdoin Glacier for
    # 2014/15 was [...] -1.96 m a-1 at [...] BH1'' (Tsutaki et al., 2016).
    melt = 1.96
    filename = 'processed/bowdoin-pressure-depth-%s.csv' % bh
    base = pd.read_csv(filename, parse_dates=True, index_col='date').squeeze()
    depth[0] = base - melt

    # return as a pandas data series
    df = pd.DataFrame(index=[date], columns=columns, data=[depth])
    df.index = df.index.rename('date')
    return df


# for each borehole
for bh, log in loggers.iteritems():

    # compute sensor depths
    filename = 'processed/bowdoin-thstring-depth-%s.csv' % bh
    depth = get_depth(bh)
    depth.to_csv(filename)

    # preprocess data logger temperatures
    # FIXME: depth was measured in 2015, temp in 2014
    filename = 'processed/bowdoin-thstring-temp-%s.csv' % bh
    temp = get_temperature(log)
    moff = ut.melt_offset(temp, depth, bh)
    temp += moff
    temp.to_csv(filename)

    # preprocess manual temperatures
    filename = 'processed/bowdoin-thstring-mantemp-%s.csv' % bh
    temp = get_temperature(log, manual=True)
    #temp += moff
    temp.to_csv(filename)

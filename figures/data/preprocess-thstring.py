#!/usr/bin/env python2

import numpy as np
import pandas as pd

loggers = {'downstream': 'Th-Bowdoin-1',
           'upstream':   'Th-Bowdoin-2'}
columns = ['temp%02d' % (i+1) for i in range(16)]


def get_temperature(log):
    """Return calibrated temperature in a data frame."""

    # input file names
    cfilename = 'original/temperature/%s_Coefs.dat' % log
    ifilename = 'original/temperature/%s_Therm.dat' % log

    # read rearranged calibration coefficients
    # sensor order downstream: BH2A[1-9] + BH2B[1-7],
    #                upstream: BH1A[1-9] + BH1B[1-4,7,5-6].
    a1, a2, a3 = np.loadtxt(cfilename, unpack=True)

    # read resistance data
    df = pd.read_csv(ifilename, skiprows=[0, 2, 3], na_values='NAN',
                     index_col=0)
    df = df[[col for col in df.columns if col.startswith('Resist')]]

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
    # FIXME: I think this was measured on 18 July 2015. Check in Martin's
    # notebook and complete the picture with measurements from 2014.

    # calculate sensor depths
    if bh == 'downstream':
        bottom = -243.7
        top = 31.25
        upper = bottom + 20.0*np.arange(9)
        lower = top + 20.0*np.arange(-6, 1)
    if bh == 'upstream':
        bottom = -265.3
        top = 13.4
        upper = bottom + 20.0*np.arange(9)
        lower = top + 20.0*np.array([-6, -5, -4, -3, 0, -2, -1])
    depth = np.hstack([upper, lower])

    # return as a pandas data series
    ts = pd.Series(index=columns, data=depth)
    return ts


# for each borehole
for bh, log in loggers.iteritems():

    # preprocess temperatures
    filename = 'processed/bowdoin-thstring-temp-%s.csv' % bh
    df = get_temperature(log)
    df.to_csv(filename)

    # compute sensor depths
    filename = 'processed/bowdoin-thstring-depth-%s.csv' % bh
    ts = get_depth(bh)
    ts.to_csv(filename)

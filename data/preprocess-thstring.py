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
    date = '2015-07-18 12:00:00'

    # Measured surfacing cable lenghts
    # * Th-Bowdoin-2: BH1A 2015-07-18 10:30, 19.70 m to 275 m mark
    #   (upstream)         2016-07-19 11:45, 21.60 m to 275 m mark
    #                 BH1B 2015-07-18 10:30, 13.40 m to sensor 7
    #                      2016-07-19 11:45, 15.30 m to sensor 7
    #
    # * Th-Bowdoin-1: BH2A 2015-07-18 12:30, 7.30 m to 250 m mark
    #   (downstream)       2016-07-19 13:20, 9.70 m to 250 m mark
    #                 BH2B 2015-07-18 12:30, 11.25 m to sensor 6
    #                      2016-07-19 13:20, 13.65 m to sensor 6

    # calculate sensor depths
    if bh == 'downstream':
        date = ['2015-07-18 12:30', '2016-07-19 13:20']
        bottom = np.array([7.30, 9.70]) - 250.0
        top =  np.array([11.25, 13.65]) + 20.0
        lower = bottom[:, None] + 20.0*np.arange(9)
        upper = top[:, None] + 20.0*np.arange(-6, 1)
    if bh == 'upstream':
        date = ['2015-07-18 10:30', '2016-07-19 11:45']
        bottom = np.array([19.70, 21.60]) - 275.0
        top =  np.array([13.40, 15.30]) + 0.0
        lower = bottom[:, None] + 20.0*np.arange(9)
        upper = top[:, None] + 20.0*np.array([-6, -5, -4, -3, 0, -2, -1])

    # lower depths make no sense; mark as unknown
    lower[:] = np.nan
    depth = -np.hstack([lower, upper])

    # return as a pandas data series
    df = pd.DataFrame(index=date, columns=columns, data=depth)
    df.index = df.index.rename('date')
    return df


# for each borehole
for bh, log in loggers.iteritems():

    # preprocess temperatures
    filename = 'processed/bowdoin-thstring-temp-%s.csv' % bh
    df = get_temperature(log)
    df.to_csv(filename)

    # compute sensor depths
    filename = 'processed/bowdoin-thstring-depth-%s.csv' % bh
    df = get_depth(bh)
    df.to_csv(filename)

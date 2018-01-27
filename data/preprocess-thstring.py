#!/usr/bin/env python2

import numpy as np
import pandas as pd
import util as ut

loggers = {'lower': 'Th-Bowdoin-1',
           'upper': 'Th-Bowdoin-2'}
columns = ['temp%02d' % (i+1) for i in range(16)]


def get_temperature(bh, log, manual=False):
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
    df.columns = [bh[0].upper() + 'T%02d' % (i+1) for i in range(16)]


    # return as dataframe
    return df


# for each borehole
for bh, log in loggers.iteritems():

    # compute sensor depths
    filename = 'processed/bowdoin-thstring-depth-%s.csv' % bh
    depth = pd.read_csv(filename, index_col='date')

    # preprocess data logger temperatures
    # FIXME: depth was measured in 2015, temp in 2014
    filename = 'processed/bowdoin-thstring-temp-%s.csv' % bh
    temp = get_temperature(bh, log)
    moff = ut.melt_offset(temp, depth, bh)
    temp += moff
    temp.to_csv(filename)

    # preprocess manual temperatures
    filename = 'processed/bowdoin-thstring-mantemp-%s.csv' % bh
    temp = get_temperature(bh, log, manual=True)
    #temp += moff
    temp.to_csv(filename)

#!/usr/bin/env python2

import numpy as np
import pandas as pd

loggers = {'downstream': 'Th-Bowdoin-1',
           'upstream':   'Th-Bowdoin-2'}

# for each borehole
for bh, log in loggers.iteritems():

    # read rearranged calibration coefficients
    # downstream: BH2A[1-9] + BH2B[1-7]
    # upstream: BH1A[1-9] + BH1B[1-4,7,5-6]
    coefpath = 'original/temperature/%s_Coefs.dat' % log
    coefs = np.loadtxt(coefpath)

    # input and output file names
    ifilename = 'original/temperature/%s_Therm.dat' % log
    ofilename = 'processed/bowdoin-temperature-%s.csv' % bh

    # read original file
    idf = pd.read_csv(ifilename, skiprows=[0, 2, 3], na_values='NAN',
                      index_col=0)

    # convert resistances to temperatures
    odf = pd.DataFrame(index=idf.index.rename('date'))
    for i in range(16):
        a1, a2, a3 = coefs[i]
        logres = np.log(idf['Resist(%d)' % (i+1)])
        odf['temp%02d' % (i+1)] = 1 / (a1 + a2*logres + a3*logres**3) - 273.15

    # write csv file
    odf.to_csv(ofilename)

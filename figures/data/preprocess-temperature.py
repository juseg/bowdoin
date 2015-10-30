#!/usr/bin/env python2

import numpy as np
import pandas as pd

# for each borehole
for bh in [1, 2]:

    # read rearranged calibration coefficients
    # borehole 1: BH2A[1-9] + BH2B[1-7]
    # borehole 2: BH1A[1-9] + BH1B[1-4,7,5-6]
    coefpath = 'original/temperature/Th-Bowdoin-%i_Coefs.dat' % bh
    coefs = np.loadtxt(coefpath)

    # input and output file names
    ifilename = 'original/temperature/Th-Bowdoin-%i_Therm.dat' % bh
    ofilename = 'processed/bowdoin-temperature-bh%d.txt' % bh

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

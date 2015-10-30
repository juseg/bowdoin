#!/usr/bin/env python2

import numpy as np
import pandas as pd

# input and output instrument names
input_instruments = ['id', 'ax', 'ay', 'mx', 'my', 'mz', 'p', 'tp', 't']
output_instruments = ['ax', 'ay', 'p', 'tp', 't']


def floatornan(x):
    try:
        return float(x)
    except ValueError:
        return np.nan

# for each borehole
for bh in [1, 2]:
    print 'Processing data for borehole %d...' % bh

    # input and output file names
    cfilename = 'original/inclino/BOWDOIN-%i_Coefs.dat' % bh
    ifilename = 'original/inclino/BOWDOIN-%i_All.dat' % bh
    ofilename = 'processed/bowdoin-inclino-bh%d.txt' % bh

    # read calibration coefficients
    coeffs = np.loadtxt(cfilename)

    # open input file
    idf = pd.read_csv(ifilename, skiprows=[0, 2, 3], index_col=0,
                      na_values='NAN')

    # convert resistances to temperatures
    odf = pd.DataFrame(index=idf.index.rename('date'))

    # these columns will need to be splitted
    rescols = [col for col in idf.columns if col.startswith('res')]
    for i, col in enumerate(rescols):

        # ifgnore columns containing no data
        if idf[col].isnull().all():
            print "col %s has only NaN, ignoring it" % col
            continue

        # split data strings into new multi-column dataframe and fill with NaN
        splitted = idf[col].str.split(',', expand=True)
        splitted.fillna(value=np.nan, inplace=True)

        # select wanted columns
        splitted.columns = input_instruments
        splitted = splitted[output_instruments]

        # replace nan values by nan
        splitted.replace('-99.199996', np.nan, inplace=True)

        # convert to numeric
        # splitted.convert_objects(convert_numeric=True)  # deprectiated
        # splitted = pd.to_numeric(splitted, errors='coerce')  # does not work
        splitted = splitted.applymap(floatornan)

        # process angles
        cx = coeffs[2*i]
        cy = coeffs[2*i+1]
        splitted['ax'] = (splitted['ax'] - cx[1])/cx[0]
        splitted['ay'] = (splitted['ay'] - cy[1])/cy[0]

        # append wanted columns to output dataframe
        newcols = [i + '0' + col[4] for i in output_instruments]
        odf[newcols] = splitted

    # write csv file
    odf.to_csv(ofilename)

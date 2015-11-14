#!/usr/bin/env python2

import numpy as np
import pandas as pd

loggers = {'downstream': 'BOWDOIN-1',
           'upstream':   'BOWDOIN-2'}
input_instruments = ['id', 'ax', 'ay', 'mx', 'my', 'mz', 'p', 'tp', 't']
output_instruments = ['ax', 'ay', 'p', 'tp', 't']



def floatornan(x):
    """Try to convert to float and return NaN if that fails."""
    try:
        return float(x)
    except ValueError:
        return np.nan


def get_data(log):
    """Return data values in a data frame."""

    # input file names
    cfilename = 'original/inclino/%s_Coefs.dat' % log
    ifilename = 'original/inclino/%s_All.dat' % log

    # read calibration coefficients
    coeffs = np.loadtxt(cfilename)

    # open input file
    idf = pd.read_csv(ifilename, skiprows=[0, 2, 3], index_col=0,
                      na_values='NAN')

    # initialize output dataframe
    odf = pd.DataFrame(index=idf.index.rename('date'))

    # these columns will need to be splitted
    rescols = [col for col in idf.columns if col.startswith('res')]

    # ignore columns containing no data
    rescols = [col for col in rescols if not idf[col].isnull().all()]

    # split remaining columns into new dataframe
    for i, col in enumerate(rescols):

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

    # return filled dataframe
    return odf


def extract_tilt(df):
    """Return tilt angles in a dataframe."""
    axcols = [col for col in df.columns if col.startswith('ax')]
    aycols = [col for col in df.columns if col.startswith('ay')]
    return df[axcols+aycols]


def extract_temp(df):
    """Return temperature values in a dataframe."""
    tcols = [col for col in df.columns if col.startswith('t0')]
    return df[tcols]


def extract_wlev_depth(df):
    """Return pressure values in a dataframe."""

    # observed water depths
    if bh == 'downstream':
        observ_date = '2014-07-22 23:40:00'
        water_depth = 0.0
        chain_design = [0.0, 10.0, 20.0, 40.0, 50.0][2:]
    if bh == 'upstream':
        observ_date = '2014-07-17 16:15:00'  # assumed
        water_depth = 46.0
        chain_design = [0.0, 7.0, 10.0, 15.0, 25.0, 35.0, 50.0][1:]

    # extract water level above sensor unit
    wlev = df[[col for col in df.columns if col.startswith('p')]]*9.80665

    # compute sensor depth using water depth from all sensors
    depth = wlev.loc[observ_date] + water_depth

    # calibrate water level
    wlev = wlev - depth + depth[0]

    # return calibrated water level and unit depth
    return wlev, depth


# for each borehole
for bh, log in loggers.iteritems():

    # get all data
    df = get_data(log)

    # extract tilt angles
    tilt = extract_tilt(df)
    tilt.to_csv('processed/bowdoin-inclino-tilt-%s.csv' % bh)

    # extract temperatures
    temp = extract_temp(df)
    temp.to_csv('processed/bowdoin-inclino-temp-%s.csv' % bh)

    # extract water level and sensor depth
    wlev, depth = extract_wlev_depth(df)
    wlev.to_csv('processed/bowdoin-inclino-wlev-%s.csv' % bh)
    depth.to_csv('processed/bowdoin-inclino-depth-%s.csv' % bh)

#!/usr/bin/env python2

import numpy as np
import pandas as pd

loggers = {'downstream': 'BOWDOIN-1',
           'upstream':   'BOWDOIN-2'}
instruments = ['id', 'ixr', 'iyr', 'mx', 'my', 'mz', 'p', 'tp', 't']
input_instruments = ['id', 'ixr', 'iyr', 'mx', 'my', 'mz', 'p', 'tp', 't']
output_instruments = ['ixr', 'iyr', 'p', 'tp', 't']


def floatornan(x):
    """Try to convert to float and return NaN if that fails."""
    try:
        return float(x)
    except ValueError:
        return np.nan


def splitstrings(ts):
    """Split series of data strings into multi-column data frame."""

    # split data strings into new multi-column dataframe and fill with NaN
    df = ts.str.split(',', expand=True)
    df.fillna(value=np.nan, inplace=True)

    # rename columns
    unitname = 'unit%02d' % int(ts.name[4:-1])
    df.columns = [instruments, [unitname]*len(instruments)]

    # replace nan values by nan
    df.replace('-99.199996', np.nan, inplace=True)

    # convert to numeric
    # splitted.convert_objects(convert_numeric=True)  # deprectiated
    # splitted = pd.to_numeric(splitted, errors='coerce')  # does not work
    df = df.applymap(floatornan)

    # return splitted dataframe
    return df



def get_data(log):
    """Return data values in a data frame."""

    # input file names
    ifilename = 'original/inclino/%s_All.dat' % log

    # open input file
    idf = pd.read_csv(ifilename, skiprows=[0, 2, 3], index_col=0,
                      parse_dates=True, na_values='NAN')

    # rename index
    idf.index = idf.index.rename('date')

    # these columns will need to be splitted
    rescols = [col for col in idf.columns if col.startswith('res')]

    # ignore columns containing no data
    rescols = [col for col in rescols if not idf[col].isnull().all()]

    # split remaining columns into new dataframe
    odf = pd.concat([splitstrings(idf[col]) for col in rescols], axis=1)

    # return filled dataframe
    return odf


def extract_tilt(df, log):
    """Return tilt angles in a dataframe."""

    # read calibration coefficients
    coefs = pd.read_csv('original/inclino/%s_Coefs.dat' % log,
                         index_col=0, comment='#')

    # keep only units present in data
    coefs = coefs.loc[df['ixr'].columns]

    # process angles and compute tilt
    tiltx = (df['ixr'] - coefs['bx'])/coefs['ax']
    tilty = (df['iyr'] - coefs['by'])/coefs['ay']
    # tilt = np.arcsin(np.sqrt(np.sin(tiltx)**2+np.sin(tilty)**2))*180/np.pi

    # return tilt
    return tiltx, tilty


def extract_temp(df):
    """Return temperature values in a dataframe."""
    temp = df['t']*1e-3
    return temp


def extract_wlev_depth(df):
    """Return water level and unit depths."""

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
    tiltunit_wlev = df['p']*9.80665

    # compute tilt unit depth using water depth from all sensors
    tiltunit_depth = tiltunit_wlev.loc[observ_date] + water_depth

    # calibration interval
    calint = {'upstream':   ['2014-07-18', '2014-07-24'],
              'downstream': ['2014-07-29', '2014-08-04']}[bh]

    # open preprocessed pressure sensor water level as a reference
    pressure_wlev = pd.read_csv('processed/bowdoin-pressure-wlev-%s.csv' % bh,
                                parse_dates=True, index_col='date').squeeze()

    # the diff between bottom tiltunit and pressure sensor over calib interval
    pressure_wlev_ref = pressure_wlev[calint[0]:calint[1]]
    tiltunit_wlev_bot = tiltunit_wlev.iloc[:,0].loc[pressure_wlev_ref.index]
    diff = pressure_wlev_ref - tiltunit_wlev_bot

    # the mean difference gives the pressure sensor depth
    pressure_depth = tiltunit_depth.iloc[0] + diff.mean()

    # reconstruct unit height from all depths
    tiltunit_height = diff.mean() + tiltunit_depth.iloc[0] - tiltunit_depth

    # calibrate water level
    tiltunit_wlev = tiltunit_wlev + tiltunit_height

    # return calibrated water level and sensor depths as dataframes
    tiltunit_depth = pd.DataFrame([tiltunit_depth])
    pressure_depth = pd.DataFrame(columns=['depth'],
                                  index=[observ_date],
                                  data=[pressure_depth])
    tiltunit_depth.index = tiltunit_depth.index.rename('date')
    pressure_depth.index = pressure_depth.index.rename('date')
    return tiltunit_wlev, tiltunit_depth, pressure_depth


# for each borehole
for bh, log in loggers.iteritems():

    # get all data
    df = get_data(log)

    # extract tilt angles
    tiltx, tilty = extract_tilt(df, log)
    tiltx.to_csv('processed/bowdoin-tiltunit-tiltx-%s.csv' % bh)
    tilty.to_csv('processed/bowdoin-tiltunit-tilty-%s.csv' % bh)

    # extract temperatures
    temp = extract_temp(df)
    temp.to_csv('processed/bowdoin-tiltunit-temp-%s.csv' % bh)

    # extract water level and sensor depth
    tu_wlev, tu_depth, pr_depth = extract_wlev_depth(df)
    tu_wlev.to_csv('processed/bowdoin-tiltunit-wlev-%s.csv' % bh)
    tu_depth.to_csv('processed/bowdoin-tiltunit-depth-%s.csv' % bh)
    pr_depth.to_csv('processed/bowdoin-pressure-depth-%s.csv' % bh)

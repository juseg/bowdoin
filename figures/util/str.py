# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin stress paper utils.
"""

import glob
import scipy.signal as sg
import pandas as pd

# Physical constants
# ------------------

SEA_DENSITY = 1029      # Sea wat. density,     kg m-3          (--)
GRAVITY = 9.80665       # Standard gravity,     m s-2           (--)


# Data loading methods
# --------------------

def is_multiline(filename):
    """Return True if file has at least two lines."""
    with open(filename) as fil:
        line = fil.readline()
        line = fil.readline()
    return line != ''


def load(filename):
    """Load preprocessed data file and return data with duplicates removed."""
    # FIXME this is a duplicate of util.tem.load
    data = pd.read_csv(filename, parse_dates=True, index_col='date')
    data = data.groupby(level=0).mean()
    return data


def load_inc(variable):
    """Load inclinometer variable data for all boreholes."""

    # load all inclinometer data for this variable
    pattern = '../data/processed/bowdoin.*.inc.' + variable + '.csv'
    data = pd.concat([load(f) for f in glob.glob(pattern)], axis=1)

    # convert water levels to pressure
    # FIXME remove water level conversion in preprocessing
    if variable == 'wlev':
        data = GRAVITY*data['20140701':]  # kPa

    # order data and drop useless records
    data = data.sort_index(axis=1, ascending=False)
    data = data.drop(['LI01', 'LI02', 'UI01'], axis=1)

    # return dataframe
    return data


def load_bowdoin_tides(order=2, cutoff=1/3600.0):
    """Return Masahiro filtered sea level in a data series."""

    # open postprocessed data series
    tide = pd.read_csv('../data/processed/bowdoin.tide.csv', index_col=0,
                       parse_dates=True, squeeze=True)

    # apply two-way lowpass filter
    tide = tide.asfreq('2s').interpolate()
    filt = sg.butter(order, cutoff, 'low')
    tide[:] = sg.filtfilt(*filt, tide)

    # return pressure data series
    return tide


def load_pituffik_tides(start='2014-07', end='2017-08'):
    """Load UNESCO IOC 5-min Pituffik tide data."""

    # find non-tempy data files
    dates = pd.date_range(start=start, end=end, freq='M')
    files = dates.strftime('../data/external/tide-thul-%Y%m.csv')
    files = [f for f in files if is_multiline(f)]

    # open in a data series
    csvkw = dict(index_col=0, parse_dates=True, header=1, squeeze=True)
    series = pd.concat([pd.read_csv(f, **csvkw) for f in files])

    # convert tide (m) to pressure (kPa)
    series = 1e-3 * SEA_DENSITY * GRAVITY * (series-series.mean())

    # return pressure data series
    return series

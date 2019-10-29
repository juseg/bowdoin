# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin tides paper utils.
"""

import scipy.signal as sg
import pandas as pd

# physical constants
g = 9.80665  # gravitational acceleration in m s-2
rhos = 1029.0  # sea water density in kg m-3


# Data loading methods
# --------------------

def has_two_lines(fname):
    """Check if given file has more than one line."""
    with open(fname) as f:
        l1 = f.readline()
        l2 = f.readline()
    result = l2 != ''
    return result


def load_bowdoin_tides(order=2, cutoff=1/3600.0):
    """Return Masahiro filtered sea level in a data series."""

    # open postprocessed data series
    ts = pd.read_csv('../data/processed/bowdoin.tide.csv', index_col=0,
                     parse_dates=True, squeeze=True)

    # apply two-way lowpass filter
    ts = ts.asfreq('2s').interpolate()
    b, a = sg.butter(order, 2*cutoff, 'low')  # order, cutoff freq
    ts[:] = sg.filtfilt(b, a, ts)

    # return pressure data series
    return ts


def load_pituffik_tides(start='2014-07', end='2017-08'):
    """Load UNESCO IOC 5-min Pituffik tide data."""

    # find non-tempy data files
    dates = pd.date_range(start=start, end=end, freq='M')
    files = dates.strftime('../data/external/tide-thul-%Y%m.csv')
    files = [f for f in files if has_two_lines(f)]

    # open in a data series
    csvkw = dict(index_col=0, parse_dates=True, header=1, squeeze=True)
    ts = pd.concat([pd.read_csv(f, **csvkw) for f in files])

    # convert tide (m) to pressure (kPa)
    ts = 1e-3*rhos*g*(ts-ts.mean())

    # return pressure data series
    return ts

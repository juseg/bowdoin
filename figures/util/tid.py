# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin tides paper utils.
"""

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

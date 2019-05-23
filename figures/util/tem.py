# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin temperature paper utils.
"""

import glob
import pandas as pd

# Global parameters
# -----------------

COLOURS = dict(bh1='C0', bh2='C1', bh3='C2', err='0.75')
MARKERS = dict(I='^', P='s', T='o')


# Data loading methods
# --------------------

def load(filename):
    """Load preprocessed data file and return data with duplicates removed."""
    data = pd.read_csv(filename, parse_dates=True, index_col='date')
    data = data.groupby(level=0).mean()
    return data


def load_all(borehole):
    """Load all temperature and depths for the given borehole."""

    # load all data for this borehole
    prefix = '../data/processed/bowdoin.' + borehole.replace('err', 'bh3')
    temp = pd.concat([load(f) for f in glob.glob(prefix+'*.temp.csv')], axis=1)
    dept = pd.concat([load(f) for f in glob.glob(prefix+'*.dept.csv')], axis=1)
    base = pd.concat([load(f) for f in glob.glob(prefix+'*.base.csv')], axis=1)

    # in this paper with ignore depth changes
    dept = dept.iloc[0]
    base = base.iloc[0].drop_duplicates().squeeze()

    # segregate BH3 erratic data
    if borehole == 'bh3':
        dept = dept[~dept.index.str.startswith('LT0')]
    elif borehole == 'err':
        dept = dept[dept.index.str.startswith('LT0')]

    # order by initial depth and remove sensors located on the surface
    cols = dept[dept > 0.0].dropna().sort_values().index.values
    dept = dept[cols]
    temp = temp[cols]

    # sensors can't be deeper than base
    dept[dept > base] = base

    # return temperature and depth
    return temp, dept, base


# Data processing methods
# -----------------------

def estimate_closure_dates(borehole, temp):
    """
    Estimate borehole closure dates from temperature time series. Look for the
    steepest cooling starting one day after the date of drilling. This seems to
    work best using daily-averaged time series. In practice this does not seem
    to work on sensors for which the beginning of the record is missing.

    Parameters
    ----------
    borehole: string
        Borehole name bh1, bh2 or bh3.
    temp: dataframe
        Daily temperature time series.
    """
    drilling_date = dict(bh1='20140716', bh2='20140717', bh3='20140722',
                         err='20140722')
    drilling_date = pd.to_datetime(drilling_date[borehole])
    closure_dates = temp[drilling_date+pd.to_timedelta('1D'):].diff().idxmin()
    closure_dates = closure_dates.mask(closure_dates == temp.index[1])
    return closure_dates

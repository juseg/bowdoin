# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin temperature paper utils.
"""

import glob
import pandas as pd
import util.com

# Global parameters
# -----------------

COLOURS = dict(bh1='C0', bh2='C1', bh3='C2', err='0.75')
MARKERS = dict(I='^', P='s', T='o')
DRILLING_DATES = dict(bh1='20140716', bh2='20140717', bh3='20140722')
PROFILES_DATES = dict(bh1=['20141001', '20170128'],
                      bh2=['20141001', '20160712'],
                      bh3=['20150101', '20151112', '20160719'],
                      err=['20150101', '20160719'])


# Data loading methods
# --------------------

def load_all(borehole):
    """Load all temperature and depths for the given borehole."""

    # load all data for this borehole
    prefix = '../data/processed/bowdoin.' + borehole.replace('err', 'bh3')
    temp = [util.com.load_file(f) for f in glob.glob(prefix+'*.temp.csv')]
    temp = pd.concat(temp, axis=1)
    dept = [util.com.load_file(f) for f in glob.glob(prefix+'*.dept.csv')]
    dept = pd.concat(dept, axis=1)
    base = [util.com.load_file(f) for f in glob.glob(prefix+'*.base.csv')]
    base = pd.concat(base, axis=1)

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


def load_manual(borehole):
    """Load manual temperature readings and mask for the given borehole."""

    # load all data for this borehole
    prefix = '../data/processed/bowdoin.' + borehole.replace('err', 'bh3')
    manu = [util.com.load_file(f) for f in glob.glob(prefix+'*.manu.csv')]
    manu = pd.concat(manu, axis=1)
    mask = [util.com.load_file(f) for f in glob.glob(prefix+'*.mask.csv')]
    mask = pd.concat(mask, axis=1).astype('bool')

    # segregate BH3 erratic data
    if borehole == 'bh3':
        manu = manu.filter(like='LT1')
        mask = mask.filter(like='LT1')
    elif borehole == 'err':
        manu = manu.filter(like='LT0')
        mask = mask.filter(like='LT0')

    # return temperature and depth
    return manu, mask


def load_profiles(borehole):
    """
    Load temperature profiles for selected dates from auto or manual data.
    """

    # load automatic data and init results dataframe
    auto, depth, base = load_all(borehole)
    dates = PROFILES_DATES[borehole]
    temp = pd.DataFrame()

    # for each date
    for date in dates:

        # use automatic data if available
        if date in auto.index:
            temp[date] = auto.loc[date].mean().dropna()

        # otherwise load manual data
        else:
            manu, mask = load_manual(borehole)
            temp[date] = manu.mask(mask).loc[date].squeeze().dropna()

    # remove depths with no data
    depth = depth[temp.index]
    return temp, depth, base


# Data processing methods
# -----------------------

def estimate_closure_state(borehole, temp):
    """
    Estimate borehole closure dates from temperature time series. Look for the
    steepest cooling starting one day after the date of drilling. This seems to
    work best using daily-averaged time series. In practice this does not seem
    to work on sensors for which the beginning of the record is missing.

    Returns a dataframe containing closure dates, the corresponding
    temperatures and time since the drilling for each unit.

    Parameters
    ----------
    borehole: string
        Borehole name bh1, bh2 or bh3.
    temp: dataframe
        Daily temperature time series.
    """
    drilling_date = DRILLING_DATES[borehole.replace('err', 'bh3')]
    drilling_date = pd.to_datetime(drilling_date)
    closure_dates = temp[drilling_date+pd.to_timedelta('1D'):].diff().idxmin()
    closure_dates = closure_dates.mask(closure_dates == temp.index[1])
    closure_temps = [temp.loc[closure_dates[k], k] for k in temp]
    return pd.DataFrame(dict(date=closure_dates, temp=closure_temps,
                             time=closure_dates-drilling_date))

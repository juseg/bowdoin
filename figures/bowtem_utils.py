# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin temperature paper utils.
"""

import cartopy.crs as ccrs  # FIXME replace with pyproj
import cartowik.decorations as cde  # FIXME replace with hyoga
import glob
import gpxpy
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
import pandas as pd

# local aliases
add_subfig_label = cde.add_subfig_label

# Global parameters
# -----------------

COLOURS = dict(bh1='C0', bh2='C1', bh3='C2', err='0.75')
MARKERS = dict(I='^', P='s', T='o')
DRILLING_DATES = dict(bh1='20140716', bh2='20140717', bh3='20140722')
PROFILES_DATES = dict(bh1=['20141001', '20170128'],
                      bh2=['20141001', '20160712'],
                      bh3=['20150101', '20151112', '20160719'],
                      err=['20150101', '20160719'])


# Plotting methods
# ----------------

def add_field_campaigns(ax=None, color='C1', ytext=None):
    """Mark 2014--2017 summer field campaigns."""

    # get axes if None provided
    ax = ax or plt.gca()

    # prepare blended transform
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)

    # for dates when people were on Bowdoin
    for start, end in [('2014-07-15', '2014-07-29'),
                       ('2015-07-06', '2015-07-20'),
                       ('2016-07-04', '2016-07-21'),
                       ('2017-07-04', '2017-07-17')]:

        # add rectangular spans
        ax.axvspan(start, end, ec='none', fc=color, alpha=0.25)

        # add text annotations
        if ytext is not None:
            duration = pd.to_datetime(end) - pd.to_datetime(start)
            midpoint = pd.to_datetime(start) + duration / 2
            ax.text(
                midpoint, ytext, midpoint.year, color=color, fontweight='bold',
                ha='center', transform=trans, clip_on=True)


def add_subfig_labels(axes=None, colors=None, **kwargs):
    """Add automatic subfigure labels (a), (b), (c), etc."""
    # NOTE: this could become part of absplots

    # get the figure axes by default, flatten arrays
    if axes is None:
        axes = plt.gcf().axes
    elif isinstance(axes, np.ndarray):
        axes = axes.flatten()

    # convert colors to list if it is a non-string sequence
    if isinstance(colors, str) or not hasattr(colors, '__iter__'):
        colors = [colors] * len(axes)

    # add subfigure labels
    for ax, color, label in zip( axes, colors, 'abcdefghijklmnopqrstuvwxyz'):
        add_subfig_label('('+label+')', ax=ax, color=color, **kwargs)


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
    temp = [load(f) for f in glob.glob(prefix+'*.temp.csv')]
    temp = pd.concat(temp, axis=1)
    dept = [load(f) for f in glob.glob(prefix+'*.dept.csv')]
    dept = pd.concat(dept, axis=1)
    base = [load(f) for f in glob.glob(prefix+'*.base.csv')]
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
    manu = [load(f) for f in glob.glob(prefix+'*.manu.csv')]
    manu = pd.concat(manu, axis=1)
    mask = [load(f) for f in glob.glob(prefix+'*.mask.csv')]
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


def load_strain_rate(borehole, freq='1D'):
    """
    Return horizontal shear strain rate from tilt relative to a start date
    or between two dates.

    Parameters
    ----------
    borehole: string
        Borehole name bh1 or bh3.
    freq: string
        Frequency to resample average tilts before time differentiation.

    Returns
    -------
    exz: series
        Strain rates in s-1.
    """

    # load borehole data
    prefix = '../data/processed/bowdoin.' + borehole.replace('err', 'bh3')
    tilx = load(prefix+'.inc.tilx.csv').resample(freq).mean()
    tily = load(prefix+'.inc.tily.csv').resample(freq).mean()

    # compute near horizontal shear strain
    exz_x = np.sin(tilx).diff()
    exz_y = np.sin(tily).diff()
    exz = np.sqrt(exz_x**2+exz_y**2)

    # convert to strain rate in a-1
    exz /= pd.to_timedelta(freq).total_seconds()

    # return strain rate
    return exz


def read_locations_dict(filename='../data/locations.gpx'):
    """Read waypoints dictionary from GPX file."""
    with open(filename, 'r') as gpx:
        return {wpt.name: wpt for wpt in gpxpy.parse(gpx).waypoints}


def read_locations(filename='../data/locations.gpx', crs=None):
    """Read waypoints dataframe from GPX file."""

    # read locations in geographic coordinates
    with open(filename, 'r') as gpx:
        attributes = [{attr: getattr(wpt, attr) for attr in wpt.__slots__}
                      for wpt in gpxpy.parse(gpx).waypoints]
    data = pd.DataFrame(attributes).dropna(axis=1, how='all').set_index('name')

    # if crs is given, append coordinates in given crs
    if crs is not None:
        xyz = data[['longitude', 'latitude', 'elevation']].values
        xyz = crs.transform_points(ccrs.PlateCarree(), *xyz.T).T
        data['x'], data['y'], data['z'] = xyz

    # remove timezone information (see gpxpy issue #182)
    # data.time = data.time.dt.tz_localize(None)
    # FIXME this should be fixed by gpxpy PR227, and indeed locations for
    # B17BH* now have zone-unaware times. However this creates a new issue,
    # where pandas cannot mix tz-aware and tz-unaware times. So we're going
    # to assume UTC time zone for points missing timezone information.
    data.time = pd.to_datetime(data.time, utc=True)

    # return locations dataframe
    return data



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

# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin temperature paper utils.
"""

import glob

import geopandas as gpd
import hyoga
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
import numpy as np
import pandas as pd
import xarray as xr

# Global parameters
# -----------------

COLOURS = {'bh1': 'C0', 'bh2': 'C1', 'bh3': 'C2', 'err': '0.75'}
MARKERS = {'I': '^', 'P': 's', 'T': 'o'}
DRILLING_DATES = {'bh1': '20140716', 'bh2': '20140717', 'bh3': '20140722'}
PROFILES_DATES = {
    'bh1': ['20141001', '20170128'],
    'bh2': ['20141001', '20160712'],
    'bh3': ['20150101', '20151112', '20160719'],
    'err': ['20150101', '20160719']}


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


def add_subfig_label(*args, ax=None, loc='nw', offset=8, **kwargs):
    """Add a subfigure label positioned by compass point. Defaults to an upper
    left (nw) corner in bold font.

    Parameters
    ----------
    text: string
        Subfigure label text.
    ax: Axes
        Axes to draw on, defaults to the current axes.
    loc: 'n', 'e', 's', 'w', 'ne', 'nw', 'se', or 'sw'.
        Compass point giving the label position.
    offset: scalar, optional
        Distance between the data point and text label.
    **kwargs:
        Additional keyword arguments are passed to annotate.
    """

    # get axes if None provided
    ax = ax or plt.gca()

    # check location keyword validity
    valid_locs = 'n', 'e', 's', 'w', 'ne', 'nw', 'se', 'sw'
    if loc not in valid_locs:
        raise ValueError(
            f'Unrecognized location {loc} not in {valid_locs}.')

    # text label position and offset relative to axes corner
    xpos = 1 if 'e' in loc else 0 if 'w' in loc else 0.5
    ypos = 1 if 'n' in loc else 0 if 's' in loc else 0.5
    xshift = 1-2*xpos
    yshift = 1-2*ypos
    offset = offset / (xshift*xshift+yshift*yshift)**0.5
    xytext = xshift*offset, yshift*offset

    # text alignement (opposite from annotations)
    halign = 'left' if 'w' in loc else 'right' if 'e' in loc else 'center'
    valign = 'bottom' if 's' in loc else 'top' if 'n' in loc else 'center'

    # add annotation
    return ax.annotate(fontweight=kwargs.pop('fontweight', 'bold'),
                       xy=(xpos, ypos), xytext=xytext,
                       textcoords='offset points', xycoords='axes fraction',
                       ha=halign, va=valign, *args, **kwargs)


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


# Annotation methods
# ------------------

def annotate_by_compass(*args, ax=None, color=None, point='ne', offset=8,
                        **kwargs):
    """
    Annotate by compass point and offset.

    Parameters
    ----------
    text: string
        Annotation label text.
    xy: (scalar, scalar)
        Coordinates of the point to annotate.
    ax: Axes
        Axes to draw on, defaults to the current axes.
    point: 'n', 'e', 's', 'w', 'ne', 'nw', 'se', or 'sw'.
        Compass point giving the annotation direction.
    offset: scalar, optional
        Distance between the data point and text label.
    **kwargs:
        Additional keyword arguments are passed to annotate.
    """

    # get axes if None provided
    ax = ax or plt.gca()

    # check location keyword validity
    valid_points = 'n', 'e', 's', 'w', 'ne', 'nw', 'se', 'sw'
    if point not in valid_points:
        raise ValueError(
            f'Unrecognized compass point {point} not in {valid_points}.')

    # text label position and relative anchor for the text box
    xpos = 1 if 'e' in point else -1 if 'w' in point else 0
    ypos = 1 if 'n' in point else -1 if 's' in point else 0
    offset = offset / (xpos*xpos+ypos*ypos)**0.5
    xytext = xpos*offset, ypos*offset
    relpos = (1-xpos)/2, (1-ypos)/2

    # text alignement
    halign = 'left' if 'e' in point else 'right' if 'w' in point else 'center'
    valign = 'bottom' if 'n' in point else 'top' if 's' in point else 'center'

    # default style; use transparent bbox for positioning
    arrowprops = {'arrowstyle': '-', 'color': color, 'relpos': relpos}
    arrowprops = arrowprops | kwargs.pop('arrowprops', {})
    bbox = {'pad': 0, 'ec': 'none', 'fc': 'none'} | kwargs.pop('bbox', {})

    # plot annotated waypoint
    return ax.annotate(arrowprops=arrowprops, bbox=bbox, color=color,
                       textcoords='offset points', xytext=xytext,
                       ha=halign, va=valign, *args, **kwargs)


def annotate_location(
        name, crs=None, marker='o', point=None, text=None, **kwargs):
    """Plot and annotate a geographic location."""
    gdf = gpd.read_file('../data/locations.gpx').set_index('name').loc[[name]]
    gdf = gdf.to_crs(crs)
    gdf.plot(marker=marker, **kwargs)
    if text is not None:
        coords = gdf.loc[name].geometry.coords[0]
        annotate_by_compass(text, coords, point=point, **kwargs)


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
    return pd.DataFrame({
        'date': closure_dates, 'temp': closure_temps,
        'time': closure_dates - drilling_date})


# Complete plot methods
# ---------------------

def plot_bowdoin_map(ax, boreholes=None, colors=None, season='spring'):
    """Draw boreholes location map with Sentinel image background."""

    # default boreholes and colors
    boreholes = boreholes or list(COLOURS.keys())[:-1]
    colors = colors or list(COLOURS.values())[:-1]

    # select default color and seasonal image
    color, image = {
        'summer': ('w', '20160808_175915_456_S2A_RGB'),
        'spring': ('k', '20170310_174129_456_S2A_RGB')}[season]

    # plot Sentinel image data
    img = xr.open_dataarray(f'../data/native/{image}.jpg').astype(int)
    img.plot.imshow(add_labels=False, ax=ax, interpolation='bilinear')

    # add camp and boreholes locations
    crs = '+proj=utm +zone=19'
    annotate_location(
        'Tent Swiss', ax=ax, color=color, crs=crs,
        point='s', marker='^',
        text='Camp')
    for bh, c in zip(boreholes, colors):
        for year in (14, 16, 17):
            annotate_location(
                f'B{year}{bh.upper()}', ax=ax, color=c, crs=crs,
                text=f'20{year}', point='se' if bh == 'bh1' else 'nw')

    # set axes properties
    ax.set_xlim(508e3, 512e3)
    ax.set_ylim(8621e3, 8626e3+2e3/3)
    ax.set_xticks([])
    ax.set_yticks([])

    # add scale bar
    img.to_dataset().hyoga.plot.scale_bar(ax=ax, color=color)


def plot_greenland_map(ax, color='k'):
    """Plot Greenland minimap with Bowdoin Glacier location."""

    # draw minimap
    crs = '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45'
    countries = hyoga.open.natural_earth(
        'admin_0_countries', 'cultural', '110m')
    greenland = countries[countries.NAME == 'Greenland'].to_crs(crs)
    greenland.plot(ax=ax, facecolor='none', edgecolor=color)
    annotate_location('Tent Swiss', crs=crs, ax=ax, color=color)

    # set axes properties
    ax.set_axis_off()
    ax.set_xlim(-1000e3, 1000e3)
    ax.set_ylim(-3500e3, -500e3)

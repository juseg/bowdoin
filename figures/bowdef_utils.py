# Copyright (c) 2015-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Bowdoin deformation paper utils."""

# FIXME this module is completely untested on recent Python versions and
# contains code that duplicate bowtem_utils.py and other projects.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from osgeo import gdal

# Global parameters
# -----------------

g = 9.80665  # gravitational acceleration in m s-2
COLOURS = dict(bh1='C0', bh2='C1', bh3='C2', err='0.75')
MARKERS = dict(I='^', P='s', T='o')
DRILLING_DATES = dict(bh1='20140716', bh2='20140717', bh3='20140722')


# Data processing methods
# -----------------------

def longest_continuous(ts):
    """Return longest continuous segment of a data series."""

    # assign group ids to continuous data segments
    groupids = (ts.notnull().shift(1) != ts.notnull()).cumsum()
    groupids[ts.isnull()] = np.nan

    # split groups and select the one with maximum size
    grouped = ts.groupby(groupids)
    longest = grouped.size().idxmax()
    ts = grouped.get_group(longest)
    return ts


def powerfit(x, y, deg, **kwargs):
    """Fit to a power law."""
    logx = np.log(x)
    logy = np.log(y)
    p = np.polyfit(logx, logy, deg, **kwargs)
    return p


def glenfit(depth, exz, g=9.80665, rhoi=910.0, slope=0.03):
    """Fit to a power law with exp(C) = A * (rhoi*g*slope)**n."""
    # FIXME: the slope (sin alpha) is an approximate value from MEASURES
    # FIXME: this results in very variable and sometimtes even negative values
    # for n. The negative values cause divide by zero encountered in power
    # runtime warnings in vsia(). A better approach would be to fix n = 3 and
    # fit for C only
    n, C = powerfit(depth, exz, 1)
    A = np.exp(C) / (rhoi*g*slope)**n
    return n, A


def vsia(depth, depth_base, n, A, g=9.80665, rhoi=910.0, slope=0.03):
    """Return simple horizontal shear velocity profile."""
    C = A * (rhoi*g*slope)**n
    v = 2*C/(n+1) * (depth_base**(n+1) - depth**(n+1))
    return v


# Methods to load borehole data
# -----------------------------

def load_all_depth(borehole):
    """Load all sensor depths in a single dataset."""

    # read depths
    temp_depth = load_depth('thstring', borehole)
    tilt_depth = load_depth('tiltunit', borehole)
    pres_depth = load_depth('pressure', borehole)
    pres_depth.index = ['pres']

    # concatenate datasets
    df = pd.concat((temp_depth, tilt_depth, pres_depth))  # FIXME?
    return df


def load_data(sensor, variable, borehole):
    """Return sensor variable data in a dataframe."""

    # check argument validity
    assert sensor in ('dgps', 'pressure', 'thstring', 'tiltunit')
    assert variable in ('base', 'depth', 'mantemp', 'temp', 'tiltx', 'tilty',
                        'wlev', 'velocity')
    assert borehole in ('both', 'lower', 'upper')

    # read data
    if borehole in bowdef_utils.boreholes:
        filename = ('../data/processed/bowdoin-%s-%s-%s.csv'
                    % (sensor, variable, borehole))
        df = pd.read_csv(filename, parse_dates=True, index_col='date')
        df = df.groupby(level=0).mean()
    elif borehole == 'both':
        dfu = bowdef_utils.load_data(sensor, variable, 'upper')
        dfl = bowdef_utils.load_data(sensor, variable, 'lower')
        df = pd.concat([dfu, dfl], axis=1)
    return df


def load_depth(sensor, borehole):
    """Return sensor depths in a data series."""
    # FIXME: this only read initial depth at the moment

    # read data as a series
    df = load_data(sensor, 'depth', borehole).iloc[0]
    return df


def load_bowtid_depth():
    ts = bowdef_utils.load_depth('tiltunit', 'both')
    ts = ts.sort_index(ascending=False)
    ts.index = [c[0::3] for c in ts.index]
    ts = ts.drop(['L1', 'L2', 'U1'])
    return ts


def load_total_strain(borehole, start, end=None, as_angle=False):
    """Return horizontal shear strain rate from tilt relative to a start date
    or between two dates."""

    # check argument validity
    assert borehole in bowdef_utils.boreholes

    # load tilt data
    tiltx = load_data('tiltunit', 'tiltx', borehole)
    tilty = load_data('tiltunit', 'tilty', borehole)

    # compute start and end values
    tx0 = tiltx[start].mean()
    ty0 = tilty[start].mean()
    if end is not None:
        tx1 = tiltx[end].mean()
        ty1 = tilty[end].mean()
    else:
        tx1 = tiltx
        ty1 = tilty

    # compute deformation rate in horizontal plane
    exz_x = np.sin(tx1)-np.sin(tx0)
    exz_y = np.sin(ty1)-np.sin(ty0)
    exz = np.sqrt(exz_x**2+exz_y**2)

    # convert to angles
    if as_angle == True:
        exz = np.arcsin(exz)*180/np.pi

    # return strain rate
    return exz


# Methods to load external data
# -----------------------------

def load_temp_sigma(site='B'):
    """Return 2014--2016 weather station air temperature in a data series."""

    # list file names
    years = [2014, 2015, 2016, 2017]
    fname = '../data/external/SIGMA_AWS_SiteB_%4d_level0_final.xls'
    files = [fname % y for y in years]

    # open in a data series
    csvkw = dict(index_col=0, usecols=[0, 3],
                 na_values=(-50, -9999), squeeze=True)
    ts = pd.concat([pd.read_excel(f, **csvkw) for f in files])

    # return temperature data series
    return ts


def load_tide_hour():
    """Load GLOSS hourly Pituffik tide data."""

    # date parser
    def parser(index):
        date_str = index[11:-1].replace(' ', '0')
        hour_str = {'1': '00', '2': '12'}[index[-1]]
        return pd.datetime.strptime(date_str+hour_str, '%Y%m%d%H')

    # read data
    skiprows = [0, 245, 976, 1709, 2440, 3171, 3902,
                4635, 5366, 6097, 6828, 7561]
    df = pd.read_fwf('../data/external/h808.dat', skiprows=skiprows,
                     index_col=0, parse_dates=True, date_parser=parser,
                     header=None, delimiter=' ', dtype=None, na_values='9999')

    # stack and reindex
    df = df.stack()
    df.index = df.index.map(lambda x: x[0] + pd.to_timedelta(x[1]-1, unit='H'))

    # convert to meter and remove mean
    df = (df-df.mean())/1e3
    return df


# Methods to open geographic data
# -------------------------------

def open_gtif(filename, extent=None):
    """Open GeoTIFF and return data and extent."""

    # open dataset
    ds = gdal.Open(filename)

    # read geotransform
    x0, dx, dxdy, y0, dydx, dy = ds.GetGeoTransform()
    assert dxdy == dydx == 0.0  # rotation parameters should be zero

    # if extent argument was not given
    if extent is None:

        # set image indexes to cover whole image
        col0 = 0  # index of first (W) column
        row0 = 0  # index of first (N) row
        cols = ds.RasterXSize  # number of cols to read
        rows = ds.RasterYSize  # number of rows to read

    # if extent argument was given
    else:

        # compute image indexes corresponding to map extent
        w, e, s, n = extent
        col0 = int((w-x0)/dx)  # index of first (W) column
        row0 = int((n-y0)/dy)  # index of first (N) row
        col1 = int((e-x0)/dx) + 1  # index of last (E) column
        row1 = int((s-y0)/dy) + 1  # index of last (S) row

        # make sure indexes are within data extent
        col0 = max(0, col0)
        row0 = max(0, row0)
        col1 = min(ds.RasterXSize, col1)
        row1 = min(ds.RasterYSize, row1)

        # compute number of cols and rows needed
        cols = col1 - col0  # number of cols needed
        rows = row1 - row0  # number of rows needed

        # compute coordinates of new origin
        x0 = x0 + col0*dx
        y0 = y0 + row0*dy

    # compute new image extent
    x1 = x0 + dx*cols
    y1 = y0 + dy*rows

    # read image data
    data = ds.ReadAsArray(col0, row0, cols, rows)

    # close dataset and return image data and extent
    ds = None
    return data, (x0, x1, y0, y1)


# Axes preparation
# ----------------


def unframe(ax, edges=['bottom', 'left']):
    """Unframe axes to leave only specified edges visible."""

    # remove background patch
    ax.patch.set_visible(False)

    # adjust bounds
    active_spines = [ax.spines[s] for s in edges]
    for s in active_spines:
        s.set_smart_bounds(True)

    # get rid of extra spines
    hidden_spines = [ax.spines[s] for s in ax.spines if s not in edges]
    for s in hidden_spines:
        s.set_visible(False)

    # set ticks positions
    ax.xaxis.set_ticks_position([['none', 'top'], ['bottom', 'both']]
                                ['bottom' in edges]['top' in edges])
    ax.yaxis.set_ticks_position([['none', 'right'], ['left', 'both']]
                                ['left' in edges]['right' in edges])

    # set label positions
    if 'right' in edges and not 'left' in edges:
        ax.yaxis.set_label_position('right')
    if 'top' in edges and not 'bottom' in edges:
        ax.xaxis.set_label_position('top')


# Timeseries elements
# -------------------

def resample_plot(ax, ts, freq, c='b'):
    """Plot resampled mean and std of a timeseries."""
    avg = ts.resample(freq).mean()
    std = ts.resample(freq).std()
    avg.plot(ax=ax, color=c, ls='-')
    # for some reason not working
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.25)


def rolling_plot(ax, ts, window, c='b'):
    """Plot rolling window mean and std of a timeseries."""
    avg = pd.rolling_mean(ts, window)
    std = pd.rolling_std(ts, window)
    avg.plot(ax=ax, color=c, ls='-')
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.25)


def plot_vsia_profile(depth, exz, depth_base, ax=None, c='k', n=101,
                      annotate=True):
    """Fit and plot tilt velocity profile."""

    # get current axes if None provided
    ax = ax or plt.gca()

    # prepare depth vector for fitting curve
    depth_fit = np.linspace(0.0, depth_base, n)

    # fit to glen's law
    n, A = al.glenfit(depth, exz)

    # compute velocity profiles
    v_fit = al.vsia(depth_fit, depth_base, n, A)
    v_obs = al.vsia(depth, depth_base, n, A)

    # plot fitted velocity profiles
    ax.plot(v_fit, depth_fit, c=c)
    ax.fill_betweenx(depth_fit, 0.0, v_fit, color=c, alpha=0.25)

    # add velocity arrows at observation points
    for d, v in zip(depth, v_obs):
        ax.arrow(0.0, d, v, 0.0, fc='none', ec=c,
                 head_width=5.0, head_length=1.0, length_includes_head=True)

    # add tilt arrows
    ax.quiver(v_obs, depth, -exz*2, np.sqrt(1-(2*exz)**2),
              angles='xy', scale=5.0)

    # add horizontal lines
    ax.axhline(0.0, c='k')
    ax.axhline(depth_base, c='k')

    # add fit values
    if annotate:
        ax.text(0.05, 0.05, r'A=%.2e$\,Pa^{-n}\,s^{-2}$, n=%.2f' % (A, n),
                transform=ax.transAxes)


# Map elements
# ------------

def shading(z, dx=None, dy=None, extent=None, azimuth=315.0, altitude=30.0,
            transparent=False):
    """Compute shaded relief map."""

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[2]-extent[3])/rows

    # convert to anti-clockwise rad
    azimuth = -azimuth*np.pi / 180.
    altitude = altitude*np.pi / 180.

    # compute cartesian coords of the illumination direction
    xlight = np.cos(azimuth) * np.cos(altitude)
    ylight = np.sin(azimuth) * np.cos(altitude)
    zlight = np.sin(altitude)

    # for transparent shades set horizontal surfaces to zero
    if transparent is True:
        zlight = 0.0

    # compute hillshade (dot product of normal and light direction vectors)
    u, v = np.gradient(z, dx, dy)
    return (zlight - u*xlight - v*ylight) / (1 + u**2 + v**2)**(0.5)


def slope(z, dx=None, dy=None, extent=None, smoothing=None):
    """Compute slope map with optional smoothing."""

    # get horizontal resolution
    if (dx is None or dy is None) and (extent is None):
        raise ValueError("Either dx and dy or extent must be given.")
    rows, cols = z.shape
    dx = dx or (extent[1]-extent[0])/cols
    dy = dy or (extent[2]-extent[3])/rows

    # optionally smooth data
    if smoothing:
        import scipy.ndimage as ndimage
        z = ndimage.filters.gaussian_filter(z, smoothing)

    # compute gradient along each coordinate
    u, v = np.gradient(z, dx, dy)

    # compute slope
    slope = (u**2 + v**2)**0.5
    return slope


def extent_from_coords(x, y):
    """Compute image extent from coordinate vectors."""
    w = (3*x[0]-x[1])/2
    e = (3*x[-1]-x[-2])/2
    s = (3*y[0]-y[1])/2
    n = (3*y[-1]-y[-2])/2
    return w, e, s, n


def coords_from_extent(extent, cols, rows):
    """Compute coordinate vectors from image extent."""

    # compute dx and dy
    (w, e, s, n) = extent
    dx = (e-w) / cols
    dy = (n-s) / rows

    # prepare coordinate vectors
    xwcol = w + 0.5*dx  # x-coord of W row cell centers
    ysrow = s + 0.5*dy  # y-coord of N row cell centers
    x = xwcol + np.arange(cols)*dx  # from W to E
    y = ysrow + np.arange(rows)*dy  # from S to N

    # return coordinate vectors
    return x, y

#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import util as ut
import numpy as np
import pandas as pd
from osgeo import gdal


# physical constants
g = 9.80665  # gravitational acceleration in m s-2

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
    if borehole in ut.boreholes:
        filename = ('../data/processed/bowdoin-%s-%s-%s.csv'
                    % (sensor, variable, borehole))
        df = pd.read_csv(filename, parse_dates=True, index_col='date')
        df = df.groupby(level=0).mean()
    elif borehole == 'both':
        dfu = ut.io.load_data(sensor, variable, 'upper')
        dfl = ut.io.load_data(sensor, variable, 'lower')
        df = pd.concat([dfu, dfl], axis=1)
    return df


def load_depth(sensor, borehole):
    """Return sensor depths in a data series."""
    # FIXME: this only read initial depth at the moment

    # read data as a series
    df = load_data(sensor, 'depth', borehole).iloc[0]
    return df


def load_bowtid_depth():
    ts = ut.io.load_depth('tiltunit', 'both')
    ts = ts.sort_index(ascending=False)
    ts.index = [c[0::3] for c in ts.index]
    ts = ts.drop(['L1', 'L2', 'U1'])
    return ts


def load_total_strain(borehole, start, end=None, as_angle=False):
    """Return horizontal shear strain rate from tilt relative to a start date
    or between two dates."""

    # check argument validity
    assert borehole in ut.boreholes

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

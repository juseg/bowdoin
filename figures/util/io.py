#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import numpy as np
import pandas as pd
from osgeo import gdal


# functions to load borehole data

def load_temp(site='B'):
    """Return 2014--2016 weather station air temperature in a data series."""

    # read data
    prefix = '../data/weather/SIGMA_AWS_Site%s_' % site
    filelist = [prefix+s for s in ['2014_level0_final.csv',
                                   '2015_level0_final.csv',
                                   '2016_level0_160824.csv']]
    datalist = [pd.read_csv(filename, parse_dates=True, index_col='Date',
                            dayfirst=True, na_values=(-50, -9999))
                            ['Temperature_1[degC]']
                for filename in filelist]
    ts = pd.concat(datalist)
    return ts


def load_all_depth(borehole):
    """Load all sensor depths in a single dataset."""

    # read depths
    temp_depth = load_depth('thstring', borehole)
    tilt_depth = load_depth('tiltunit', borehole)
    pres_depth = load_depth('pressure', borehole)
    pres_depth.index = ['pres']

    # concatenate datasets
    df = pd.concat((temp_depth, tilt_depth, pres_depth))
    return df


def load_all_temp(borehole, freq='1D'):
    """Load all temperatures in a single dataset."""

    # read temperature values
    temp_temp = load_data('thstring', 'temp', borehole).resample(freq).mean()
    tilt_temp = load_data('tiltunit', 'temp', borehole).resample(freq).mean()

    # concatenate datasets
    df = pd.concat((temp_temp, tilt_temp), axis=1)
    return df


def load_data(sensor, variable, borehole):
    """Return sensor variable data in a dataframe."""

    # check argument validity
    assert sensor in ('dgps', 'pressure', 'thstring', 'tiltunit')
    assert variable in ('depth', 'mantemp', 'temp', 'tiltx', 'tilty',
                        'wlev', 'velocity')
    assert borehole in ('downstream', 'upstream')

    # read data
    filename = ('../data/processed/bowdoin-%s-%s-%s.csv'
                % (sensor, variable, borehole))
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    return df


def load_depth(sensor, borehole):
    """Return sensor depths in a data series."""

    # read first depth measurement
    df = load_data(sensor, 'depth', borehole).iloc[0]
    return df


def load_strain_rate(borehole, freq, as_angle=False):
    """Return horizontal shear strain rate from tilt at given frequency."""

    # check argument validity
    assert borehole in ('downstream', 'upstream')

    # load tilt data
    tiltx = load_data('tiltunit', 'tiltx', borehole).resample(freq).mean()
    tilty = load_data('tiltunit', 'tilty', borehole).resample(freq).mean()

    # compute horizontal shear strain
    exz_x = np.sin(tiltx).diff()
    exz_y = np.sin(tilty).diff()
    exz = np.sqrt(exz_x**2+exz_y**2)

    # convert to angles
    if as_angle == True:
        exz = np.arcsin(exz)*180/np.pi

    # convert to strain rate
    dt = pd.to_timedelta(freq).total_seconds()
    dt /= 365.0 * 24 * 60 * 60
    exz /= dt

    # return strain rate series
    return exz


def load_total_strain(borehole, start, end=None, as_angle=False):
    """Return horizontal shear strain rate from tilt relative to a start date
    or between two dates."""

    # check argument validity
    assert borehole in ('downstream', 'upstream')

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


# functions to open geographic data

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

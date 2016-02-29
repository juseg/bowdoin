#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

import numpy as np
import pandas as pd


def load_data(sensor, variable, borehole):
    """Return sensor variable data in a dataframe."""

    # check argument validity
    assert sensor in ('dgps', 'pressure', 'thstring', 'tiltunit')
    assert variable in ('depth', 'temp', 'tiltx', 'tilty', 'wlev', 'velocity')
    assert borehole in ('downstream', 'upstream')

    # read data
    filename = ('data/processed/bowdoin-%s-%s-%s.csv'
                % (sensor, variable, borehole))
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    return df


def load_depth(sensor, borehole):
    """Return sensor depths in a data series."""

    # read data
    df = load_data(sensor, 'depth', borehole)
    return df


def load_strain_rate(borehole, freq, as_angle=False):
    """Return horizontal shear strain rate from tilt at given frequency."""

    # check argument validity
    assert borehole in ('downstream', 'upstream')

    # load tilt data
    tiltx = load_data('tiltunit', 'tiltx', borehole).resample(freq)
    tilty = load_data('tiltunit', 'tilty', borehole).resample(freq)

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

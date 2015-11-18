#!/usr/bin/env python2
# coding: utf-8

"""Data input functions."""

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



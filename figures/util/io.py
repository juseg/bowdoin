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


def longest_continuous(ts):
    """Return longest continuous segment of a data series."""

    # assign group ids to continuous data segments
    groupids = (ts.notnull().shift(1) != ts.notnull()).cumsum()
    groupids[ts.isnull()] = np.nan

    # split groups and select the one with maximum lenght
    groups = groupids.groupby(groupids)
    maxlen = groups.cumcount().max()
    end = groups.cumcount().idxmax()
    start = end - maxlen

    # return subset data series
    return ts[start:end]

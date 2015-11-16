#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd


# parameters

boreholes = ['upstream', 'downstream']
colors = ['b', 'r']


# data input functions

def load_data(sensor, variable, borehole):
    """Return sensor variable data in a dataframe."""

    # check argument validity
    assert sensor in ('dgps', 'pressure', 'thstring', 'tiltunit')
    assert variable in ('temp', 'tilt', 'wlev', 'velocity')
    assert borehole in ('downstream', 'upstream')

    # read data
    filename = ('data/processed/bowdoin-%s-%s-%s.csv'
                % (sensor, variable, borehole))
    df = pd.read_csv(filename, parse_dates=True, index_col='date')
    return df


def load_depth(sensor, borehole):
    """Return sensor depths in a data series."""

    # check argument validity
    assert sensor in ('dgps', 'pressure', 'thstring', 'tiltunit')
    assert borehole in ('downstream', 'upstream')

    # read data
    filename = ('data/processed/bowdoin-%s-depth-%s.csv'
                % (sensor, borehole))
    ds = pd.read_csv(filename, header=None, index_col=0, squeeze=True)
    return ds


# plotting funcions


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


def rollplot(ax, arg, window, c='b'):
    """Plot rolling mean and std of a variable."""

    mean = pd.rolling_mean(arg, window)
    std = pd.rolling_std(arg, window)
    arg.plot(ax=ax, color=c, ls='', marker='.', markersize=0.5)
    mean.plot(ax=ax, color=c, ls='-')
    ax.fill_between(arg.index, mean-2*std, mean+2*std, color=c, alpha=0.1)

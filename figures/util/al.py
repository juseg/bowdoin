#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt

"""Data analysis functions."""


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

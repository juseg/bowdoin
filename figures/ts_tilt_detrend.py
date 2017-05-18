#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut


def seriesfit(ts, deg, imin=None, imax=None, **kwargs):
    """Fit data series by a polynomial between imin and imax."""

    # extract integer dates and data values
    x = ts.index.astype(int)
    y = ts.values

    # exctact non-nan values over desired interval for polyfit
    xclean = ts[imin:imax].dropna().index.astype(int)
    yclean = ts[imin:imax].dropna().values

    # perform polynomial fit
    if len(xclean) != 0:
        p = np.polyfit(xclean, yclean, deg, **kwargs)
        v = np.polyval(p, x)
        fit = pd.Series(index=ts.index, data=v)
    else:
        fit = ts.copy()

    # return new series or empty series
    return fit


def framefit(df, deg, imin=None, imax=None, **kwargs):
    """Fit each series in dataframe by a polynomial between imin and imax."""
    fit = df.copy()
    for col in fit.columns:
        fit[col] = seriesfit(fit[col], deg, imin=imin, imax=imax, **kwargs)
    return fit


def detrend_series(ts, imin=None, imax=None):
    """Detrend data series between imin and imax."""
    trend = seriesfit(ts[imin:imax], 1, imin=None, imax=None)
    ts -= trend
    return ts


def detrend_dataframe(df, imin=None, imax=None):
    """Detrend each series in dataframe between imin and imax."""
    trend = framefit(df, 1, imin=imin, imax=imax)
    df -= trend
    return df


# reference dates
d0 = '2014-11-01'
d1 = '2015-11-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[bh]

    # plot tilt unit temperature
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh)[d0:]
    tilty = ut.io.load_data('tiltunit', 'tilty', bh)[d0:]

    # compute reference values
    tx0 = tiltx[d0].mean()
    ty0 = tilty[d0].mean()
    tx1 = tiltx[d1].mean()
    ty1 = tilty[d1].mean()

    # detrend
    tiltx = detrend_dataframe(tiltx, imin=d0, imax=d1)
    tilty = detrend_dataframe(tilty, imin=d0, imax=d1)

    # compute tilt relative to reference
    tilt = np.arcsin(np.sqrt(np.sin(tiltx)**2+np.sin(tilty)**2))*180/np.pi
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel('detrended tilt ' + bh)
    ax.set_ylim(0.0, 0.2)

# save
ut.pl.savefig(fig)

#!/usr/bin/env python2
# coding: utf-8

"""Plotting tools."""

import pandas as pd


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


def resample_plot(ax, ts, freq, c='b'):
    """Plot resampled mean and std of a timeseries."""
    avg = ts.resample(freq, how='mean')
    std = ts.resample(freq, how='std')
    avg.plot(ax=ax, color=c, ls='-')
    # for some reason not working
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.2)


def rolling_plot(ax, ts, window, c='b'):
    """Plot rolling window mean and std of a timeseries."""
    avg = pd.rolling_mean(ts, window)
    std = pd.rolling_std(ts, window)
    avg.plot(ax=ax, color=c, ls='-')
    ax.fill_between(avg.index, avg-2*std, avg+2*std, color=c, alpha=0.2)

#!/usr/bin/env python2
# coding: utf-8

"""Plotting tools."""

import numpy as np
import pandas as pd
import util as ut
import al


# functions to create a figure

def subplots_inches(nrows=1, ncols=1, figsize=None,
                    left=None, bottom=None, right=None, top=None,
                    wspace=None, hspace=None, projection=None, **kwargs):
    from matplotlib.pyplot import rcParams, subplots

    # get figure dimensions from rc params if missing
    figw, figh = figsize or rcParams['figure.figsize']

    # normalize inner spacing to axes dimensions
    if wspace is not None:
        wspace = (((figw-left-right)/wspace+1)/ncols-1)**(-1)
    if hspace is not None:
        hspace = (((figh-bottom-top)/hspace+1)/nrows-1)**(-1)

    # normalize outer margins to figure dimensions
    if left is not None:
        left = left/figw
    if right is not None:
        right = 1-right/figw
    if bottom is not None:
        bottom = bottom/figh
    if top is not None:
        top = 1-top/figh

    # pass projection argument to subplot keywords
    subplot_kw = kwargs.pop('subplot_kw', {})
    if projection is not None:
        subplot_kw['projection'] = projection

    # return figure and subplot grid
    return subplots(nrows=nrows, ncols=ncols, figsize=figsize,
                    gridspec_kw={'left': left, 'right': right,
                                 'bottom': bottom, 'top': top,
                                 'wspace': wspace, 'hspace': hspace},
                    subplot_kw=subplot_kw, **kwargs)


def subplots_mm(nrows=1, ncols=1, figsize=None,
                left=None, bottom=None, right=None, top=None,
                wspace=None, hspace=None, projection=None, **kwargs):

    # convert all non null arguments in inches
    mm = 1/25.4
    if figsize is not None:
        figw, figh = figsize
        figsize = (figw*mm, figh*mm)
    if left is not None:
        left*=mm
    if right is not None:
        right*=mm
    if bottom is not None:
        bottom=bottom*mm
    if top is not None:
        top=top*mm
    if wspace is not None:
        wspace=wspace*mm
    if hspace is not None:
        hspace=hspace*mm

    # use inches helper to align subplots
    return subplots_inches(nrows=nrows, ncols=ncols, figsize=figsize,
                           left=left, right=right, bottom=bottom, top=top,
                           wspace=wspace, hspace=hspace,
                           projection=projection, **kwargs)


# functions to modify axes properties

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


# functions to plot data

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

def plot_campaigns(ax, y=0.0):
    """Plot 2014--2016 summer field campaigns."""

    # add rectangular spans
    # FIXME: evtl. correct date after departure 2016
    c = ut.palette['darkorange']
    ax.axvspan('2014-07-15', '2014-07-29', ec='none', fc=c, alpha=0.25)
    ax.axvspan('2015-07-06', '2015-07-20', ec='none', fc=c, alpha=0.25)
    ax.axvspan('2016-07-04', '2016-07-21', ec='none', fc=c, alpha=0.25)

    # add text annotations
    # FIXME: use hybrid coordinates
    props = dict(color=c)
    ax.text('2014-07-10', y, 'f.c. 2014', ha='left', color=c)
    ax.text('2015-07-13', y, 'f.c. 2015', ha='center', color=c)
    ax.text('2016-07-26', y, 'f.c. 2016', ha='right', color=c)

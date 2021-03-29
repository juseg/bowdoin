# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin stress paper utils.
"""

import glob
import numpy as np
import scipy.signal as sg
import pandas as pd
import absplots as apl
import matplotlib as mpl
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import util.com

# Physical constants
# ------------------

SEA_DENSITY = 1029      # Sea wat. density,     kg m-3          (--)
GRAVITY = 9.80665       # Standard gravity,     m s-2           (--)


# Data loading methods
# --------------------

def is_multiline(filename):
    """Return True if file has at least two lines."""
    with open(filename) as fil:
        line = fil.readline()
        line = fil.readline()
    return line != ''


def load(variable='wlev'):
    """Load inclinometer variable data for all boreholes."""

    # load all inclinometer data for this variable
    pattern = '../data/processed/bowdoin.*.inc.' + variable + '.csv'
    data = [util.com.load_file(f) for f in glob.glob(pattern)]
    data = pd.concat(data, axis=1)

    # convert water levels to pressure
    # FIXME remove water level conversion in preprocessing
    if variable == 'wlev':
        data = GRAVITY*data['20140701':]  # kPa

    # order data and drop useless records
    data = data.sort_index(axis=1, ascending=False)
    data = data.drop(['LI01', 'LI02', 'UI01'], axis=1)

    # return dataframe
    return data


def load_freezing_dates(fraction=0.75):
    """Load freezing dates."""

    # load hourly temperature data
    temp = util.str.load(variable='temp').resample('1H').mean()

    # remove a long-term warming tail
    for unit, series in temp.items():
        temp[unit] = series.where(series.index < series.idxmin())

    # compute date when temp has reached fraction of min
    date = abs(temp-fraction*temp.min()).idxmin()

    # return as freezing dates
    return date


def load_bowdoin_tides(order=2, cutoff=1/3600.0):
    """Return Masahiro filtered sea level in a data series."""

    # open postprocessed data series
    tide = pd.read_csv('../data/processed/bowdoin.tide.csv', index_col=0,
                       parse_dates=True, squeeze=True)

    # apply two-way lowpass filter
    tide = tide.asfreq('2s').interpolate()
    filt = sg.butter(order, cutoff, 'low')
    tide[:] = sg.filtfilt(*filt, tide)

    # return pressure data series
    return tide


def load_pituffik_tides(start='2014-07', end='2017-08', unit='kPa'):
    """Load UNESCO IOC 5-min Pituffik tide data."""

    # find non-tempy data files
    dates = pd.date_range(start=start, end=end, freq='M')
    files = dates.strftime('../data/external/tide-thul-%Y%m.csv')
    files = [f for f in files if is_multiline(f)]

    # open in a data series
    csvkw = dict(index_col=0, parse_dates=True, header=1, squeeze=True)
    series = pd.concat([pd.read_csv(f, **csvkw) for f in files])

    # convert tide (m) to pressure (kPa)
    if unit == 'm':
        return series
    if unit == 'kPa':
        return 1e-3 * SEA_DENSITY * GRAVITY * (series-series.mean())

    # otherwise raise exception
    raise ValueError("Invalid unit {}.".format(unit))



# Signal processing
# -----------------

def filter(pres, order=4, cutoff=1/24, btype='high'):
    """Apply butterworth filter on entire dataframe."""

    # prepare filter (order, cutoff)
    filt = sg.butter(order, cutoff, btype=btype)

    # for each unit
    for unit in pres:

        # crop, filter and reindex
        series = pres[unit].dropna()
        series[:] = sg.filtfilt(*filt, series)
        series = series.reindex_like(pres)
        pres[unit] = series

    # return filtered dataframe
    return pres


# Figure initialization
# ---------------------

def subplots_fourier():
    """Prepare 2x10 subplots with optimized locations."""

    # initialize figure with 2x3x4 subplots grid
    fig = apl.figure_mm(figsize=(180, 120))
    axes = np.array([fig.subplots_mm(  # 40x35 mm panels
        nrows=3, ncols=4, sharex=True, sharey=True, gridspec_kw=dict(
            left=10, right=2.5, bottom=7.5, top=2.5, hspace=2.5, wspace=2.5)),
                     fig.subplots_mm(  # 20x10 mm panels
        nrows=3, ncols=4, sharex=True, sharey=False, gridspec_kw=dict(
            left=27.5, right=5, bottom=25, top=5, hspace=22.5, wspace=22.5))])

    # hide 2x2x1 unused axes in the top-right corner
    for ax in axes[:, :2, 3].flat:
        ax.set_visible(False)

    # reshape to 12x2 and delete invisible axes
    axes = axes.reshape(2, -1).T
    axes = np.delete(axes, [3, 7], 0)

    # add subfigure labels on main axes
    util.com.add_subfig_labels(axes[:, 0])

    # set log scale on all axes
    for ax in axes.flat:
        ax.set_xscale('log')

    # mark all the insets
    for axespair in axes:
        mark_inset(*axespair, loc1=2, loc2=4, ec='0.75', ls='--')

    # set tidal ticks, no labels on insets
    for ax in axes[:, 1]:
        ax.set_xlim(0.4, 1.4)
        ax.set_xticks([12/24, 12.42/24, 23.93/24, 25.82/24])
        ax.set_xticks([], minor=True)
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    # move tide axes upwards
    for ax in axes[-1]:
        ax.set_position(ax.get_position().translated(0, 5/120))

    # set labels on last main axes
    ax = axes[-1, 0]
    ax.set_xlabel('xlabel', labelpad=7)
    ax.set_ylabel('ylabel', labelpad=0)
    ax.yaxis.label.set_position((10, 2+(3.75-5)/35))
    ax.yaxis.label.set_va('top')

    # annotate tidal modes on last inset axes
    ax = axes[-1, 1]
    blended = mpl.transforms.blended_transform_factory(
        ax.transData, ax.transAxes)
    kwargs = dict(ha='center', xycoords=blended, textcoords='offset points')
    ax.annotate('Tidal constituents', xy=(16/24, 1), xytext=(0, 36), **kwargs)
    kwargs.update(arrowprops=dict(arrowstyle='-'))
    ax.annotate(r'$S_2$', xy=(12.00/24, 1), xytext=(-12, 20), **kwargs)
    ax.annotate(r'$M_2$', xy=(12.42/24, 1), xytext=(+00, 20), **kwargs)
    ax.annotate(r'$N_2$', xy=(12.55/24, 1), xytext=(+12, 20), **kwargs)
    ax.annotate(r'$K_1$', xy=(23.93/24, 1), xytext=(-4, 20), **kwargs)
    ax.annotate(r'$O_1$', xy=(25.82/24, 1), xytext=(+4, 20), **kwargs)

    # return figure and axes
    return fig, axes


def subplots_specgram(nrows=10):
    """Initialize subplots for spectrograms and the like."""

    # initialize figure
    pd.plotting.register_matplotlib_converters()
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=nrows, sharex=True, sharey=True,
        gridspec_kw=dict(
            left=12.5, right=12.5, bottom=12.5, top=2.5, hspace=1))

    # add subfigure labels
    util.com.add_subfig_labels(axes)

    # show only the outside spines
    for ax in axes:
        ax.spines['top'].set_visible(ax.is_first_row())
        ax.spines['bottom'].set_visible(ax.is_last_row())
        ax.tick_params(bottom=ax.is_last_row(), which='both')

    # return figure and axes
    return fig, axes

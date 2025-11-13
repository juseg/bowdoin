# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""
Bowdoin stress paper utils.
"""

import glob
import argparse
import itertools
import multiprocessing
import os.path
import sys
import time

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd
import scipy.signal as sg
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

import bowtem_utils

# Physical constants
# ------------------

SEA_DENSITY = 1029      # Sea wat. density,     kg m-3          (--)
GRAVITY = 9.80665       # Standard gravity,     m s-2           (--)


# Parallel MultiPlotter class
# ---------------------------

class MultiPlotter():
    """Plot multiple figures in parallel."""

    def __init__(self, plotter, **options):
        """Initialize with a plot method and options dictionary."""
        self.plotter = plotter
        self.options = options

    def __call__(self):
        """Plot and save figures in parallel."""
        options = vars(self.parse())
        iterargs = itertools.product(*options.values())
        with multiprocessing.Pool() as pool:
            pool.starmap(self.savefig, iterargs)
        # unfortunately starmap can't take iterable keyword-arguments
        # iterkwargs = [dict(zip(options, combi)) for combi in iterargs]

    def parse(self):
        """Parse command-line arguments."""
        parser = argparse.ArgumentParser(description=__doc__)
        for name, choices in self.options.items():
            parser.add_argument(
                f'-{name}[0]', f'--{name}', choices=choices, default=choices,
                nargs='+')
        return parser.parse_args()

    def savefig(self, *args):
        """Plot and save one figure."""
        filename = '_'.join([sys.argv[0][:-3]] + list(args))
        basename = os.path.basename(filename)
        print(time.strftime(f'[%H:%M:%S] plotting {basename} ...'))
        fig = self.plotter(*args)
        fig.savefig(filename, dpi='figure')
        mpl.pyplot.close(fig)


# Data loading methods
# --------------------

def is_multiline(filename):
    """Return True if file has at least two lines."""
    with open(filename, encoding='utf-8') as fil:
        line = fil.readline()
        line = fil.readline()
    return line != ''


def load(interp=False, filt=None, resample=None, tide=False, variable='wlev'):
    """Load inclinometer variable data for all boreholes."""

    # load all inclinometer data for this variable
    pattern = '../data/processed/bowdoin.*.inc.' + variable + '.csv'
    data = [bowtem_utils.load(f) for f in glob.glob(pattern)]
    data = pd.concat(data, axis=1)

    # convert water levels to pressure
    # FIXME remove water level conversion in preprocessing
    if variable == 'wlev':
        data = GRAVITY*data['20140701':]  # kPa

    # order data and drop useless records
    if variable != 'base':
        data = data.sort_index(axis=1, ascending=False)
        data = data.drop(['LI01', 'LI02', 'UI01'], axis=1)

    # resample
    if resample is not None:
        data = data.resample(resample).mean()

    # load tide data
    if tide is True:
        assert resample is not None
        data['tide'] = load_pituffik_tides().resample(resample).mean() / 10

    # resample
    if interp is True:
        data = data.interpolate(limit_area='inside').dropna(how='all')

    # apply filter (4h high cutoff gives max correlations over 20140916-1016).
    if filt in ('12hbp', '12hhp', '24hbp', '24hhp'):
        assert resample is not None
        perday = pd.to_timedelta(resample).total_seconds() / 3600 / 24
        lowcut = perday if filt.startswith('24h') else 2*perday
        cutoff = lowcut if filt.endswith('hp') else (lowcut, 6*perday)
        btype = 'highpass' if filt.endswith('hp') else 'bandpass'
        data = butter(data, cutoff=cutoff, btype=btype)
    elif filt == 'deriv':
        assert resample is not None
        data = data.diff() / pd.to_timedelta(resample).total_seconds() * 1e3

    # return dataframe
    return data


def load_freezing_dates(fraction=0.8):
    """Load freezing dates."""

    # load hourly temperature data
    temp = load(variable='temp').resample('1h').mean()

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
                       parse_dates=True).squeeze('columns')

    # apply two-way lowpass filter
    tide = tide.asfreq('2s').interpolate()
    filt = sg.butter(order, cutoff, 'low')
    tide[:] = sg.filtfilt(*filt, tide)

    # return pressure data series
    return tide


def load_pituffik_tides(start='2014-07', end='2017-08', unit='kPa'):
    """Load UNESCO IOC 5-min Pituffik tide data."""

    # find non-tempy data files
    dates = pd.date_range(start=start, end=end, freq='ME')
    files = dates.strftime('../data/external/tide-thul-%Y%m.csv')
    files = [f for f in files if is_multiline(f)]

    # open in a data series
    series = pd.concat([pd.read_csv(
        f, index_col=0, parse_dates=True, header=1).squeeze('columns')
            for f in files])

    # convert tide (m) to pressure (kPa)
    if unit == 'm':
        return series
    if unit == 'kPa':
        return 1e-3 * SEA_DENSITY * GRAVITY * (series-series.mean())

    # otherwise raise exception
    raise ValueError(f"Invalid unit {unit}.")


# Signal processing
# -----------------

def butter(pres, order=4, cutoff=1/24, btype='high'):
    """Apply butterworth filter on entire dataframe."""

    # prepare filter (order, cutoff)
    filt = sg.butter(order, cutoff, btype=btype)

    # for each unit
    for unit in pres:

        # except the tide
        if unit != 'tide':

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
    axes = np.array([
        fig.subplots_mm(  # 40x35 mm panels
            nrows=3, ncols=4, sharex=True, sharey=True, gridspec_kw={
                'left': 10, 'right': 2.5, 'bottom': 7.5, 'top': 2.5,
                'hspace': 2.5, 'wspace': 2.5}),
        fig.subplots_mm(  # 20x10 mm panels
            nrows=3, ncols=4, sharex=True, sharey=False, gridspec_kw={
                'left': 27.5, 'right': 5, 'bottom': 25, 'top': 5,
                'hspace': 22.5, 'wspace': 22.5})])

    # hide 2x2x1 unused axes in the top-right corner
    for ax in axes[:, :2, 3].flat:
        ax.set_visible(False)

    # reshape to 12x2 and delete invisible axes
    axes = axes.reshape(2, -1).T
    axes = np.delete(axes, [3, 7], 0)

    # add subfigure labels on main axes
    bowtem_utils.add_subfig_labels(axes[:, 0])

    # set log scale on all axes
    for ax in axes.flat:
        ax.set_xscale('log')

    # mark all the insets
    # FIXME replace with ax.indicate_inset()
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
    kwargs = {
        'ha': 'center', 'xycoords': blended, 'textcoords': 'offset points'}
    ax.annotate('Tidal constituents', xy=(16/24, 1), xytext=(0, 36), **kwargs)
    kwargs.update(arrowprops={'arrowstyle': '-'})
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
        gridspec_kw={
            'left': 12.5, 'right': 12.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 1})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes)

    # show only the outside spines
    for ax in axes:
        ax.spines['top'].set_visible(ax.get_subplotspec().is_first_row())
        ax.spines['bottom'].set_visible(ax.get_subplotspec().is_last_row())
        ax.tick_params(bottom=ax.get_subplotspec().is_last_row(), which='both')

    # return figure and axes
    return fig, axes


def subsubplots(fig, axes, nrows=10):
    """Add open-spine sub-plots within each parent axes."""
    hspace_mm = 1
    subaxes = np.array([ax.get_subplotspec().subgridspec(
        ncols=1, nrows=nrows,
        hspace=nrows/(fig.get_position_mm(ax)[3] / hspace_mm + 1 - nrows)
        ).subplots() for ax in axes])

    # hide parent axes and reimplement sharex and sharey
    for pax, panel in zip(axes, subaxes):
        pax.set_axis_off()
        for ax in panel:
            ax.sharex(pax)
            ax.sharey(pax)

    # only show subaxes outer spines
    for ax in subaxes.flat:
        ax.patch.set_visible(False)
        ax.spines['top'].set_visible(ax.get_subplotspec().is_first_row())
        ax.spines['bottom'].set_visible(ax.get_subplotspec().is_last_row())
        ax.tick_params(bottom=ax.get_subplotspec().is_last_row(), which='both')

        # move the grid to background ghost axes
        ax.grid(False)
        ax = fig.add_subplot(ax.get_subplotspec(), sharex=ax, sharey=ax)
        ax.grid(which='minor')
        ax.patch.set_visible(False)
        ax.set_zorder(-1)
        ax.tick_params(which='both', **{k: False for k in [
            'labelleft', 'labelbottom', 'left', 'bottom']})
        for spine in ax.spines.values():
            spine.set_visible(False)

    # return the subaxes
    return subaxes

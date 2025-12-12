#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress periodograms."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd
import scipy as sp

import bowstr_utils
import bowtem_utils


def compute_fft(series):
    """Compute fast Fourier transform periodogram."""
    amplitude = np.abs(np.fft.rfft(series.values))[1:]
    frequency = np.fft.rfftfreq(series.shape[-1], 1)[1:]
    period = series.index.freq / pd.to_timedelta('1D') / frequency
    return period, amplitude


def compute_lsp(series, periods):
    """Compute Lomb-Scargle periodogram ready for plotting."""
    frequency = 2 * np.pi / periods
    time = (series.index - series.index[0]).total_seconds()
    power = sp.signal.lombscargle(time, series, frequency)
    amplitude = 2 * (power / len(periods))**0.5
    return periods / 24 / 3600, amplitude


def compute_periodogram(series, periods, method='fft'):
    """Compute custom periodogram ready for plotting."""
    series = series.dropna()
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]
    func = globals().get(f'compute_{method}')
    args = (series,) + (periods,) * (method == 'lsp')
    return func(*args)


def plot(method='stfft'):
    """Plot and return full figure for given options."""

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

    # load stress and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    date = bowstr_utils.load_freezing_dates()
    df = bowstr_utils.load_spectral(
        interp=True, resample='1h', variable=method[:2])

    # for each tilt unit
    for i, unit in enumerate(df):
        color = f'C{i}'

        # plot periodograms (FIXME replace LSP power with amplitude)
        per, amp = compute_periodogram(
            df.loc[date.get(unit, None):, unit],
            np.logspace(-1, 3, 201)*24*3600, method=method[2:])
        axes[i, 0].plot(per, amp, color=color)
        per, amp = compute_periodogram(
            df.loc[date.get(unit, None):, unit],
            np.logspace(-0.35, 0.1, 201)*24*3600, method=method[2:])
        axes[i, 1].plot(per, amp, color=color)

        # set axes properties
        # if method == 'fft':
        axes[i, 1].set_ylim(np.array([-0.05, 1.05])*amp[per < 2].max())
        axes[i, 0].text(
            0.95, 0.35, 'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m',
            color=color, fontsize=6, fontweight='bold',
            transform=axes[i, 0].transAxes, ha='right')

    # add labels
    axes[-1, 0].set_xlabel('period (days)')
    axes[-1, 0].set_ylabel(
        f'\namplitude of {'tilt' if method[:2] == 'ti' else 'stress'} change'
        f'\nafter borehole closure ({'k°' if method[:2] == 'ti' else 'kPa'}'
        r'$\,s^{-1}$)')
    axes[-1, 0].text(
        0.95, 0.1, r'Pituffik tide$\,/\,$10', color='C9', fontsize=6,
        fontweight='bold', ha='right', transform=axes[-1, 0].transAxes)
    axes[-1, 0].yaxis.label.set_va('top')
    axes[-1, 0].yaxis.label.set_position((10, 2+(3.75-5)/35))

    # set log scale on all axes
    for ax in axes.flat:
        ax.set_xscale('log')

    # mark all the insets
    for axespair in axes:
        axespair[0].indicate_inset(inset_ax=axespair[1], ls='dashed')

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

    # annotate tidal modes on last inset
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

    # return figure
    return fig


def main():
    """Main program called during execution."""
    methods = ['stlsp', 'stfft', 'tilsp', 'tifft']
    plotter = bowstr_utils.MultiPlotter(plot, methods=methods)
    plotter()


if __name__ == '__main__':
    main()

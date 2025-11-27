#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress periodograms."""

import numpy as np
import pandas as pd
import scipy as sp
import bowstr_utils


def compute_fft(series):
    """Compute fast Fourier transform ready for plotting."""
    # FIXME review this code, is diff() truly needed?

    # interpolate, drop nans, and differentiate
    series = series.dropna()
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]  # first value is nan after diff

    # prepare frequencies and periods
    frequency = np.fft.rfftfreq(series.shape[-1], 1)

    # compute real fft amplitude
    rfft = np.fft.rfft(series.values)
    amplitude = np.abs(rfft)

    # to compute spectral power or gain
    # power = amplitude**2
    # gain = 10*np.log10(power)

    # remove zero frequency, convert to periods
    period = (1/frequency[1:]) * (series.index.freq/pd.to_timedelta('1D'))
    amplitude = amplitude[1:]

    # return periods and amplitude
    return period, amplitude


def compute_lsp(series, periods):
    """Compute Lomb-Scargle periodogram ready for plotting."""

    # interpolate, drop nans, and differentiate
    series = series.interpolate(limit_area='inside')
    series = series.dropna()
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]  # first value is nan after diff

    # prepare frequencies and periods
    frequency = 2 * np.pi / periods

    # compute periodogram
    time = (series.index-series.index[0]).total_seconds()
    power = sp.signal.lombscargle(time, series, frequency)
    # amplitude = (4*power/len(periods))**0.5  # maybe

    # return spectral power
    return periods / 24 / 3600, power


def compute_periodogram(series, periods, method='fft'):
    """Compute custom periodogram ready for plotting."""
    func = globals().get(f'compute_{method}')
    args = (series,) + (periods,) * (method == 'lsp')
    return func(*args)


def load(variable='press', **kwargs):
    """Load modified variables."""
    if variable == 'press':
        data = bowstr_utils.load(tide=True, variable='wlev', **kwargs)
    else:
        tilx = bowstr_utils.load(tide=True, variable='tilx', **kwargs)
        tily = bowstr_utils.load(tide=False, variable='tily', **kwargs)
        tide = tilx.pop('tide')
        tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
        tilt = tilt * 1e3
        data = tilt.assign(tide=tide)
    return data


def plot(variable='press', method='fft'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig, axes = bowstr_utils.subplots_fourier()

    # load stress and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    date = bowstr_utils.load_freezing_dates()
    df = load(variable=variable, interp=True, resample='1h')

    # for each tilt unit
    for i, unit in enumerate(df):
        color = f'C{i}'

        # plot periodograms (FIXME replace LSP power with amplitude)
        per, amp = compute_periodogram(
            df.loc[date.get(unit, None):, unit],
            np.logspace(-1, 3, 201)*24*3600, method=method)
        axes[i, 0].plot(per, amp, color=color)
        per, amp = compute_periodogram(
            df.loc[date.get(unit, None):, unit],
            np.logspace(-0.35, 0.1, 201)*24*3600, method=method)
        axes[i, 1].plot(per, amp, color=color)

        # set axes properties
        axes[i, 1].set_ylim(np.array([-0.05, 1.05])*amp[per < 2].max())
        axes[i, 0].text(
            0.95, 0.35, 'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m',
            color=color, fontsize=6, fontweight='bold',
            transform=axes[i, 0].transAxes, ha='right')

    # add labels
    axes[-1, 0].set_xlabel('period (days)')
    axes[-1, 0].text(
        0.95, 0.1, r'Pituffik tide$\,/\,$10', color='C9', fontsize=6,
        fontweight='bold', ha='right', transform=axes[-1, 0].transAxes)
    axes[-1, 0].yaxis.set_label_text(
        f'amplitude of {variable.replace('press', 'stress')} change\n'
        f'after borehole closure ({'kPa' if variable == 'stres' else 'k°'}'
        r'$\,s^{-1}$)')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    methods = ['fft', 'lsp']
    variables = ['press', 'tilts']
    plotter = bowstr_utils.MultiPlotter(
        plot, variables=variables, methods=methods)
    plotter()


if __name__ == '__main__':
    main()

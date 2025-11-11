#!/usr/bin/env python
# Copyright (c) 2021-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress wavelet transforms."""

import numpy as np
import matplotlib as mpl
import pywt
import bowstr_utils


def wavelets(series, ax):
    """Plot continuous wavelet transform from data series."""

    # interpolate, drop nans, and differentiate
    series = series.dropna()

    # compute wavelet widths
    # width = omega*samplefreq / (2*waveletfreq*np.pi)
    # width = omega*waveletperiod/timestep / (2*np.pi)
    periods = np.arange(1, 36)  # periods in hours
    # widths = 5*periods*pd.to_timedelta('1h')/series.index.freq / (2*np.pi)

    # compute wavelet transform
    scales = periods  # FIXME not sure about that
    cwt, _ = pywt.cwt(series, scales, 'morl')

    # plot wavelet transform
    extent = (
        *mpl.dates.date2num((series.index[0], series.index[-1])),
        periods[0], periods[-1])
    vmax = np.quantile(abs(cwt), 0.99)
    ax.imshow(
        cwt, cmap='RdBu', aspect='auto', extent=extent, origin='lower',
        vmin=-vmax, vmax=vmax)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = bowstr_utils.subplots_specgram(nrows=8)

    # load stress data
    depth = bowstr_utils.load(variable='dept').iloc[0]
    date = bowstr_utils.load_freezing_dates()
    pres = bowstr_utils.load(highpass=True, interp=True, resample='10min', tide=True)
    pres = pres.drop(columns=['UI03', 'UI02'])
    pres = pres['20150501':'20151101']
    tide = pres.pop('tide')

    # interpolate, drop nans, differentiate and filter
    # (I'm not sure filtering is really useful here)
    pres = pres.diff()
    pres = pres.div(pres.index.to_series().diff().dt.total_seconds(), axis=0)

    # for each unit
    for i, unit in enumerate(pres):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'
        series = pres[unit][date[unit]:]

        # plot wavelet transform
        wavelets(series, ax)

        # add text label
        ax.text(
            1.01, 0, f'{unit}\n{depth[unit]:.0f}'r'$\,$m',
            color=color, fontsize=6, fontweight='bold', transform=ax.transAxes)

    # plot tide data (diff but no filter)
    ax = axes[-1]
    tide = tide.diff()
    tide = tide.div(pres.index.to_series().diff().dt.total_seconds(), axis=0)
    wavelets(tide, ax)

    # add text label
    ax.text(
        1.01, 0, 'Pituffik\ntide'+r'$\,/\,$10',
        color='C9', fontsize=6, fontweight='bold', transform=ax.transAxes)

    # plot invisible timeseries to format axes as pandas
    # force pandas date format
    (10+0*series.resample('1D').mean()).plot(ax=ax, visible=False)

    # set axes properties
    ax.set_ylabel('period (h)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

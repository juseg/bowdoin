#!/usr/bin/env python
# Copyright (c) 2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress wavelet transforms."""

import numpy as np
import pandas as pd
import matplotlib as mpl
import pywt
import util.str


def wavelets(series, ax):
    """Plot continuous wavelet transform from data series."""

    # interpolate, drop nans, and differentiate
    series = series.interpolate(limit_area='inside').dropna()

    # compute wavelet widths
    # width = omega*samplefreq / (2*waveletfreq*np.pi)
    # width = omega*waveletperiod/timestep / (2*np.pi)
    periods = np.arange(1, 36)  # periods in hours
    widths = 5*periods*pd.to_timedelta('1h')/series.index.freq / (2*np.pi)

    # compute wavelet transform
    scales = periods  # FIXME not sure about that
    cwt, frequencies = pywt.cwt(series, scales, 'morl')

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
    fig, axes = util.str.subplots_specgram(nrows=8)

    # load stress data
    depth = util.str.load(variable='dept').iloc[0]
    date = util.str.load_freezing_dates()
    pres = util.str.load().resample('10min').mean()  # kPa
    pres = pres.drop(columns=['UI03', 'UI02'])
    pres = pres['20150501':'20151101']

    # interpolate, drop nans, differentiate and filter
    # (I'm not sure filtering is really useful here)
    pres = pres.interpolate(limit_area='inside').dropna()
    pres = pres.diff()
    pres = pres.div(pres.index.to_series().diff().dt.total_seconds(), axis=0)
    pres = util.str.filter(pres, cutoff=1/6/24)

    # for each unit
    for i, unit in enumerate(pres):
        ax = axes[i]
        color = 'C{}'.format(i+2*(i > 3))
        series = pres[unit][date[unit]:]

        # plot wavelet transform
        wavelets(series, ax)

        # add text label
        ax.text(
            1.01, 0, unit+'\n'+r'{:.0f}$\,$m'.format(depth[unit]),
            color=color, fontsize=6, fontweight='bold', transform=ax.transAxes)

    # plot tide data (diff but no filter)
    ax = axes[-1]
    tide = util.str.load_pituffik_tides().resample('10min').mean() / 10  # kPa/10
    tide = tide.interpolate(limit_area='inside').dropna()
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

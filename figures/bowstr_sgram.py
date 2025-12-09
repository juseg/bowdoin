#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress spectrograms."""

import absplots as apl
import numpy as np
import pandas as pd
import matplotlib as mpl

import bowstr_utils


def plot_spectrogram(series, ax, color):
    """Plot spectrogram from data series."""

    # differentiate series
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]

    # plot spectrogram (values range ca. -170 to -50)
    per, freqs, bins, img = ax.specgram(
        series, Fs=pd.to_timedelta('1D') / series.index.freq, NFFT=6*24*14,
        noverlap=6*24*12, cmap='Greys', vmin=-150, vmax=-50)

    # shift image horizontally to series start date
    offset = mpl.dates.date2num(series.index[0])
    img.set_extent((*img.get_extent()[:2]+offset, *img.get_extent()[2:]))

    # plot 22-26 vs 10-14 hour bands power ratio
    pow12 = per[(24/14 <= freqs) & (freqs <= 24/10), :].sum(axis=0)
    pow24 = per[(24/26 <= freqs) & (freqs <= 24/22), :].sum(axis=0)
    index = pd.DatetimeIndex(mpl.dates.num2date(offset+bins))
    ratio = 1 / (1 + pow24 / pow12)
    ratio = pd.Series(ratio, index=index)
    ratio = ratio.where(pow12 > 1e-15).resample('2D').mean()
    (1+ratio).plot(ax=ax, color='w', lw=2, alpha=0.5)
    (1+ratio).plot(ax=ax, color=color)


def load(variable='st', **kwargs):
    """Load modified variables."""
    if variable == 'st':
        data = bowstr_utils.load(tide=True, variable='wlev', **kwargs)
    else:
        tilx = bowstr_utils.load(tide=True, variable='tilx', **kwargs)
        tily = bowstr_utils.load(tide=False, variable='tily', **kwargs)
        tide = tilx.pop('tide')
        tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
        tilt = tilt * 1e3
        data = tilt.assign(tide=tide)
    return data


def plot(method='stfft'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig, pax = apl.subplots_mm(figsize=(180, 120), gridspec_kw={
        'left': 10, 'right': 7.5, 'bottom': 10, 'top': 2.5})
    axes = bowstr_utils.subsubplots(fig, [pax], nrows=8)[0]

    # load stress and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    dates = bowstr_utils.load_freezing_dates()
    df = load(interp=True, resample='10min', variable=method[:2])
    df = df.drop(columns=['UI03', 'UI02'])

    # plot spectrograms and text labels
    for i, unit in enumerate(df):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'
        series = df.loc[dates.get(unit, None):, unit]
        plot_spectrogram(series, ax, color)
        ax.text(
            1.02, 0.5, 'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

    # set axes properties
    ax.set_xlim('20140701', '20170801')
    ax.set_ylim(0.5, 2.5)
    ax.set_yticks([1, 2])
    ax.set_yticklabels(['24', '12'])
    axes[4].set_ylabel('period (h)', ha='left', labelpad=0)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    methods = ['stfft', 'tifft']
    plotter = bowstr_utils.MultiPlotter(plot, methods=methods)
    plotter()


if __name__ == '__main__':
    main()

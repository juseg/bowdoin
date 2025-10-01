#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress spectrograms."""

import pandas as pd
import matplotlib as mpl
import absplots as apl
import util.str


def specgram(series, ax, color):
    """Plot specgrogram from data series."""

    # interpolate, drop nans, and differentiate
    series = series.interpolate(limit_area='inside').dropna()
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]  # first value is nan after diff

    # calculate sampling frequency in hours
    freq = pd.to_timedelta('1D') / series.index.freq

    # plot spectrogram (values range ca. -170 to -50)
    per, freqs, bins, img = ax.specgram(
        series, Fs=freq, NFFT=6*24*14, noverlap=6*24*12,
        cmap='Greys', vmin=-150, vmax=-50)

    # shift the image horizontally to series start date
    # (this is all we need as long as freq is in days)
    offset = mpl.dates.date2num(series.index[0])
    img.set_extent((*img.get_extent()[:2]+offset, *img.get_extent()[2:]))

    # power in 12 vs 24-h bands (resample needed for pandas format ticks)
    pow12 = per[(24/14 <= freqs) & (freqs <= 24/10), :].sum(axis=0)
    pow24 = per[(24/26 <= freqs) & (freqs <= 24/22), :].sum(axis=0)
    ratio = pow12 / (pow12 + pow24)
    index = pd.DatetimeIndex(mpl.dates.num2date(offset+bins))
    ratio = pd.Series(ratio, index=index)
    ratio = ratio.resample('1D').mean().interpolate()
    (1+ratio).plot(ax=ax, color='w', lw=2, alpha=0.5)
    (1+ratio).plot(ax=ax, color=color)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = util.str.subplots_specgram(nrows=8)

    # load stress and freezing dates
    depth = util.str.load(variable='dept').iloc[0]
    date = util.str.load_freezing_dates()
    pres = util.str.load().resample('10min').mean()  # kPa
    pres = pres.drop(columns=['UI03', 'UI02'])

    # for each tilt unit
    for i, unit in enumerate(pres):
        ax = axes[i]
        color = 'C{}'.format(i+2*(i > 3))
        series = pres[unit][date[unit]:]

        # plot spectrogram
        specgram(series, ax, color)

        # add text label
        ax.text(
            1.01, 0, unit+'\n'+r'{:.0f}$\,$m'.format(depth[unit]),
            color=color, fontsize=6, fontweight='bold', transform=ax.transAxes)

    # plot tide data
    ax = axes[-1]
    tide = util.str.load_pituffik_tides().resample('10min').mean() / 10  # kPa/10
    specgram(tide, ax, color='C9')

    # add text label
    ax.text(
        1.01, 0, 'Pituffik\ntide'+r'$\,/\,$10',
        color='C9', fontsize=6, fontweight='bold', transform=ax.transAxes)

    # plot invisible timeseries to format axes as pandas
    # (the 1D frequency ensures compatibility with mdates.date2num)
    series.resample('1D').mean().plot(ax=ax, visible=False)

    # set axes properties
    ax.set_xlim('20140615', '20170815')
    ax.set_ylim(0.5, 2.5)
    ax.set_yticks([1, 2])
    ax.set_yticklabels(['24', '12'])

    # set y label
    axes[4].set_ylabel('period (h)', y=0)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

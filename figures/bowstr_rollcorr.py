#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress rolling-window cross-correlation."""

import numpy as np
import pandas as pd
import matplotlib as mpl
import util.str


def crosscorr(series, other, wmin=-30, wmax=6):
    """Compute cross-correlation between two series."""
    shifts = np.arange(wmin, wmax+1)
    dataframe = pd.DataFrame(
        data=[series.shift(i, freq='infer') for i in shifts],
        index=pd.to_timedelta(shifts*series.index.freq))
    return dataframe.corrwith(other, axis=1)


def rollcorr(series, other, window='14D', stride='7D'):
    """Compute rolling-window cross-correlation between two series."""
    window = pd.to_timedelta(window)
    starts = pd.date_range(
        start=series.index[0], end=series.index[-1]-window, freq=stride)
    slices = [slice(start, start+window) for start in starts]
    corr = pd.DataFrame(
        data=[crosscorr(series[s], other[s]) for s in slices],
        index=starts+window/2,
        ).transpose()
    return corr


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = util.str.subplots_specgram(nrows=7)

    # load stress data
    depth = util.str.load(variable='dept').iloc[0]
    pres = util.str.load().resample('10min').mean()  # kPa
    pres = pres.interpolate(limit_area='inside')
    pres = util.str.filter(pres, cutoff=(1/6/12, 1/6), btype='bandpass')

    # load tide data
    tide = util.str.load_pituffik_tides().resample('10min').mean() / 10  # kPa/10

    # subset
    pres = pres.drop(columns=['UI03', 'UI02'])
    # pres = pres['20140901':'20150901']  # first year looks good
    # tide = tide['20140901':'20150901']  # things get messy then

    # for each unit
    for i, unit in enumerate(pres):
        color = 'C{}'.format(i+2*(i > 3))
        series = pres[unit].dropna()

        # plot cross correlation
        ax = axes[i]
        corr = rollcorr(series, tide)
        ax.imshow(
            corr, alpha=0.75, aspect='auto', cmap='RdGy_r', vmin=-1, vmax=1,
            extent=(*mpl.dates.date2num((corr.columns[0], corr.columns[-1])),
                    *-corr.index[[-1, 0]].total_seconds()/3600))

        # find maximum (anti)correlation
        delay = -np.abs(corr).dropna(axis=1, how='all').idxmax()
        delay = delay.dt.total_seconds()/3600
        delay = delay.where(np.abs(corr).max() >= 0.5)
        delay = delay.resample('1D').nearest()  # for compat with mpl.dates
        delay.plot(ax=ax, drawstyle='steps-mid', color='w', lw=2, alpha=0.5)
        delay.plot(ax=ax, drawstyle='steps-mid', color=color)

        # add text label
        ax.text(
            1.01, 0, unit+'\n'+r'{:.0f}$\,$m'.format(depth[unit]),
            color=color, fontsize=6, fontweight='bold', transform=ax.transAxes)

    # set axes properties
    ax.set_xlim('20140615', '20170815')
    ax.set_yticks([0, 2, 4])
    axes[len(axes)//2].set_ylabel('phase delay (h)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

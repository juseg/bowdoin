#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util.str
import numpy as np
import pandas as pd
import absplots as apl


def crosscorr(series, other, window=36):
    """Return cross correlation between two series."""
    shifts = np.arange(-window/2, window/2+1)
    df = pd.DataFrame(
        data=[series.shift(i, freq='infer') for i in shifts],
        index=pd.to_timedelta(shifts*series.index.freq))
    return df.corrwith(other, axis=1)


def crosscorr_df(dataframe):
    """Return cross correlation between series of a dataframe."""
    other = dataframe[dataframe.columns[0]]
    df = pd.DataFrame(
        data=[crosscorr(series, other) for series in dataframe])
    return df


def groupcorr(series, other):
    grouped = series.groupby(series.index.month)
    applied = grouped.apply(crosscorr, other)
    applied = applied.unstack(level=0)
    return applied


def rollcorr(series, other, window='14D', stride='7D'):
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
    pd.plotting.register_matplotlib_converters()
    fig, axes = apl.subplots_mm(
        figsize=(180, 120), nrows=4, sharex=True, gridspec_kw=dict(
            left=12.5, right=12.5, bottom=12.5, top=2.5, hspace=2.5))

    # load pressure data
    pres = util.str.load()['20150101':'20170101']
    pres = pres.resample('10T').mean().interpolate()
    pres = pres[['UI07', 'UI06', 'UI05', 'UI04']]
    pres = util.str.filter(pres, cutoff=(1/6/12, 1/6), btype='bandpass')

    # for each unit
    for i, unit in enumerate(pres):
        color = 'C{}'.format(i)
        ts = pres[unit]

        # plot cross correlation
        ax = axes[i]
        corr = rollcorr(ts, pres['UI07'])
        ax.pcolormesh(corr.columns, corr.index.total_seconds()/3600, corr,
                      alpha=0.75, cmap='Greys', shading='auto', vmin=0, vmax=1)

        # find maximum correlation
        xlim = ax.get_xlim()
        shift = corr.idxmax().dt.total_seconds()/3600
        shift.plot(ax=ax, color=color, drawstyle='steps-mid')
        ax.set_xlim(xlim)

        # deactivate grids
        ax.grid(False)

    # set axes properties
    ax.set_ylabel('phase shift (h)')
    ax.set_xlabel('date')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

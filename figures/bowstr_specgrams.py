#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util.str
import pandas as pd
import matplotlib.dates as mdates
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(180, 90), nrows=10, sharex=True, sharey=True,
        gridspec_kw=dict(
            left=12.5, right=20, bottom=12.5, top=2.5, hspace=2.5))
    cax = fig.add_axes_mm([180-17.5, 12.5, 2.5, 90-15])

    # get freezing dates
    t = util.str.load(variable='temp')['20140717':].resample('1H').mean()
    df = abs(t-(0.1*t.max()+0.9*t.min())).idxmin()  # date of freezing

    # for each tilt unit
    p = util.str.load()
    for i, u in enumerate(p):
        ax = grid[i]
        c = 'C%d' % i

        # crop, resample, and interpolate
        ts = p[u][df[u]:].dropna().resample('1H').mean()
        ts = ts.interpolate().diff()[1:]/3.6

        # calculate sample frequency
        dt = (ts.index[1]-ts.index[0])/pd.to_timedelta('1H')
        fs = 1 / dt

        # ensure same kwargs with last (tide) plot
        kwargs = dict(
            Fs=fs, NFFT=24*8, noverlap=0,
            cmap='Greys', interpolation='nearest', vmin=-40, vmax=20)

        # plot spectrogram
        _, _, _, im = ax.specgram(
            ts, xextent=mdates.date2num([ts.index[0], ts.index[-1]]), **kwargs)

        # add corner tag
        ax.text(0.95, 0.2, u, color=c, transform=ax.transAxes,
                bbox=dict(ec='none', fc='w', alpha=0.75, pad=1))

        # set axes properties
        ax.set_ylim(0.5/24, 2.5/24)
        ax.set_yticks([1/24, 1/12])
        ax.set_yticklabels(['24', '12'])

    # plot tide data
    ax = grid.flat[-1]
    ts = util.str.load_pituffik_tides().resample('1H').mean()
    ts = ts.interpolate().diff()[1:]/3.6
    _, _, _, im = ax.specgram(
        ts, xextent=mdates.date2num([ts.index[0], ts.index[-1]]), **kwargs)
    ax.text(0.95, 0.2, 'Tide', color='k', transform=ax.transAxes,
            bbox=dict(ec='none', fc='w', alpha=0.75, pad=1))

    # plot invisible timeseries to format axes as pandas
    # (the 1D frequency ensures compatibility with mdates.date2num)
    ts.resample('1D').mean().plot(ax=ax, visible=False)

    # set axes properties
    ax.set_ylim(2.5/24, 0.5/24)
    ax.set_yticks([1/24, 1/12])
    ax.set_yticklabels(['24', '12'])

    # add colorbar
    cb = fig.colorbar(im, cax=cax, extend='both')
    cb.set_label(r'pressure change ($Pa\,s^{-1}$) power spectral density (dB)')

    # set axes properties
    grid[5].set_ylabel('period (h)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

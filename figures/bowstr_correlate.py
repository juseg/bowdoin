#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import numpy as np
import pandas as pd
import absplots as apl
import util.com
import util.str


def crosscorr(series, other, wmin=-72*1.5, wmax=72*1.5):
    """Return cross correlation for multiple lags."""
    shifts = np.arange(wmin, wmax+1)
    df = pd.DataFrame(
        data=[series.shift(i, freq='infer') for i in shifts],
        index=pd.to_timedelta(shifts*series.index.freq))
    return df.corrwith(other, axis=1)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=3, gridspec_kw=dict(
        left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=17.5))

    # add subfigure labels
    util.com.add_subfig_labels(grid, loc='sw')

    # load pressure data
    depth = util.str.load(variable='dept').iloc[0]
    pres = util.str.load().resample('10T').mean().interpolate()  # kPa
    pres = util.str.filter(pres, cutoff=(1/6/12, 2/6), btype='bandpass')

    # load tide data
    tide = util.str.load_pituffik_tides().resample('10T').mean() / 10
    pres = pres['20140916':'20141016']
    tide = tide['20140916':'20141016']

    # plot time series
    offsets = 5 * (1+np.arange(len(pres.columns)))[::-1]
    (pres+offsets).plot(ax=grid[0], legend=False)
    tide.plot(ax=grid[0], c='C9')

    # for each unit
    for i, unit in enumerate(pres):
        c = 'C%d' % i
        ts = pres[unit]

        # plot (series.plot with deltas affected by #18910)
        ax = grid[1]
        xcorr = crosscorr(ts, tide)
        delay = -xcorr.index.total_seconds()/3600
        ax.plot(delay, xcorr)

        # find maximum correlation
        # (a positive shift corresponds to a negative delay)
        shift = abs(xcorr).idxmax()
        delay = -shift.total_seconds()/3600
        value = xcorr[shift]
        ax.plot(delay, value, c=c, marker='o')

        # plot phase delays
        ax = grid[2]
        ax.plot(delay, depth[unit], c=c, marker='o')
        ax.text(delay+0.1, depth[unit]-1.0, unit, color=c, clip_on=True)

    # set axes properties
    grid[0].set_ylim(-5, 47.5)
    grid[0].set_ylabel('pressure (kPa)')
    grid[1].axvline(0.0, ls=':')
    grid[1].set_xticks([-12, 0, 12])
    grid[1].set_xlabel('time delay (h)')
    grid[1].set_ylabel('cross-correlation')
    grid[2].axvline(0.0, ls=':')
    grid[2].set_xlim(0.5, 3.5)
    grid[2].invert_yaxis()
    grid[2].set_xlabel('phase delay (h)')
    grid[2].set_ylabel('sensor depth (m)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

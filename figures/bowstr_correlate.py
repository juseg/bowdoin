#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress cross-correlation."""

import numpy as np
import pandas as pd
import absplots as apl
import bowtem_utils
import bowstr_utils


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
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=3, gridspec_kw={
        'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
        'wspace': 17.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(grid, loc='sw')

    # load stress data
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(highpass=True, interp=True, resample='10min', tide=True)
    pres = pres['20140916':'20141016']

    # plot time series
    offsets = 5 * np.arange(len(pres.columns))[::-1]
    (pres+offsets).plot(ax=grid[0], legend=False)
    tide = pres.pop('tide')

    # for each unit
    for i, unit in enumerate(pres):
        color = f'C{i}'
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
        ax.plot(delay, value, c=color, marker='o')

        # plot phase delays
        ax = grid[2]
        ax.plot(delay, depth[unit], c=color, marker='o')
        ax.text(delay+0.1, depth[unit]-1.0, unit, color=color, clip_on=True)

    # set axes properties
    grid[0].set_ylim(-5, 47.5)
    grid[0].set_ylabel('stress (kPa)')
    grid[1].axvline(0.0, ls=':')
    grid[1].set_xticks([-12, 0, 12])
    grid[1].set_xlabel('time delay (h)')
    grid[1].set_ylabel('cross-correlation')
    grid[2].axvline(0.0, ls=':')
    grid[2].set_xlim(0.5, 3.5)
    grid[2].invert_yaxis()
    grid[2].set_xlabel('phase delay (h)')
    grid[2].set_ylabel('sensor depth (m)')

    # remove empty headlines in date tick labels
    grid[0].set_xticks(grid[0].get_xticks(), [
        label.get_text()[1:] for label in grid[0].get_xticklabels()])

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

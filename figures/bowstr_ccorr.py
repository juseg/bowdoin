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


def plot(filt='24hhp'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=3, gridspec_kw={
        'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
        'wspace': 17.5})
    subaxes = bowstr_utils.subsubplots(fig, grid[:1])[0]

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=subaxes[9], loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=grid[1], loc='sw')
    bowtem_utils.add_subfig_label('(c)', ax=grid[2], loc='sw')

    # load stress data
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(
        filt=filt, interp=True, resample='10min', tide=True)
    pres = pres['20140916':'20141016']

    # plot time series
    for i, unit in enumerate(pres):
        ax = subaxes[i]
        color = f'C{i}'
        pres[unit].plot(ax=ax, color=color, legend=False)

        # set axes properties
        ax.get_lines()[0].set_clip_box(grid[0].bbox)
        ax.set_ylim((-.2, .2) if filt == 'deriv' else (-2, 2))
        ax.set_yticks([-.1, .1] if filt == 'deriv' else (-1, 1))
        ax.tick_params(labelleft=ax.get_subplotspec().is_last_row())

    # for each non-tide unit
    tide = pres.pop('tide')
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
    grid[1].axvline(0.0, ls=':')
    grid[1].set_xticks([-12, 0, 12])
    grid[1].set_xlabel('time delay (h)')
    grid[1].set_ylabel('cross-correlation')
    grid[2].axvline(0.0, ls=':')
    grid[2].set_xlim(0.5, 3.5)
    grid[2].invert_yaxis()
    grid[2].set_xlabel('phase delay (h)')
    grid[2].set_ylabel('sensor depth (m)')

    # set labels and remove empty headlines in date tick labels
    subaxes[4].set_ylabel(
        'stress change (Pa/s)' if filt == 'deriv' else 'stress (kPa)')
    subaxes[9].set_xlabel('')
    subaxes[9].set_xticks(subaxes[9].get_xticks(), [
        label.get_text()[1:] for label in subaxes[9].get_xticklabels()])

    # return figure
    return fig


def main():
    """Main program called during execution."""
    filters = ['12hbp', '12hhp', '24hbp', '24hhp', 'deriv']  # FIXME 'phase'
    plotter = bowstr_utils.MultiPlotter(plot, filters=filters)
    plotter()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation cross-correlation."""

import numpy as np
import pandas as pd
import absplots as apl
import bowdef_utils
import bowtem_utils
import bowstr_utils


def crosscorr(series, other, wmin=-72*1.5, wmax=72*1.5):
    """Return cross correlation for multiple lags."""
    shifts = np.arange(wmin, wmax+1)
    df = pd.DataFrame(
        data=[series.shift(i, freq='infer') for i in shifts],
        index=pd.to_timedelta(shifts*series.index.freq))
    return df.corrwith(other, axis=1)


def plot(method='inner'):
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.subplots_mm(ncols=1, gridspec_kw={
        'left': 10, 'right': 127.5, 'bottom': 12.5, 'top': 2.5})
    fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 72.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5, 'wspace': 15})
    subaxes = bowstr_utils.subsubplots(
        fig, fig.axes[:1], nrows=8, sharey=False)[0]

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=subaxes[-1], loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], loc='sw')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[2], loc='sw')

    # load depth and tilt rates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    tilt = bowdef_utils.load_multivariate(join=method)
    tilt = tilt['20150516':'20150815']
    tilt = tilt.dropna(how='all', axis=1)

    # plot time series
    for i, unit in enumerate(tilt):
        ax = subaxes[i]
        color = 'tab:cyan' if unit == 'vh' else f'C{i}'
        tilt[unit].plot(ax=ax, color=color, legend=False)
        ax.text(
            1.08, 0.5,
            '\nSurface\nspeed\n'r'($m\,a^{-1}$)' if unit == 'vh' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(fig.axes[0].bbox)
        ax.set_ylim((250, 650) if unit == 'vh' else (2, 13))
        ax.set_yticks([300, 600] if unit == 'vh' else [5, 10])
        ax.tick_params(labelleft=len(subaxes)-i in (1, 2))

    # for each non-tide unit
    gnss = tilt.pop('vh')
    for i, unit in enumerate(tilt):
        color = f'C{i}'
        ts = tilt[unit]

        # plot (series.plot with deltas affected by #18910)
        ax = fig.axes[1]
        shift = 36 / pd.to_timedelta(ts.index.freq).total_seconds() * 3600
        xcorr = crosscorr(ts, gnss, wmin=-shift, wmax=shift)
        ax.plot(-xcorr.index.total_seconds()/3600, xcorr)

        # find maximum correlation (a positive shift is a negative delay)
        shift = abs(xcorr).idxmax()
        delay = -shift.total_seconds()/3600
        ax.plot(delay, xcorr[shift], c=color, marker='o')

        # plot phase delays
        ax = fig.axes[2]
        ax.plot(delay, depth[unit], c=color, marker='o')
        ax.text(delay+0.1, depth[unit]-1.0, unit, color=color, clip_on=True)

    # set axes properties
    fig.axes[1].axvline(0.0, ls=':')
    fig.axes[1].set_xticks(range(-36, 48, 12))
    fig.axes[1].set_xlabel('time delay (h)')
    fig.axes[1].set_ylabel('cross-correlation', labelpad=0)
    fig.axes[1].xaxis.set_major_formatter(lambda x, pos: f'{x:g}'*(pos % 2))
    fig.axes[1].yaxis.set_major_formatter(lambda y, pos: f'{y:g}'*(pos % 2))
    fig.axes[2].axvline(0.0, ls=':')
    fig.axes[2].invert_yaxis()
    fig.axes[2].set_xlabel('phase delay (h)')
    fig.axes[2].set_ylabel('sensor depth (m)')

    # set labels and remove empty headlines in date tick labels
    subaxes[4].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    subaxes[-1].set_xlabel('')

    # save partial
    # fig.axes[1].set_visible(False)
    # fig.axes[2].set_visible(False)
    # fig.savefig(f'{__file__[:-3]}_{filt}_01')
    # fig.axes[1].set_visible(True)
    # fig.savefig(f'{__file__[:-3]}_{filt}_02')
    # fig.axes[2].set_visible(True)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    methods = ['inner', 'mixed', 'outer']
    plotter = bowstr_utils.MultiPlotter(plot, methods=methods)
    plotter()


if __name__ == '__main__':
    main()

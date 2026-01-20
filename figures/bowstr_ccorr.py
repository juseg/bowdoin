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
    fig = apl.figure_mm(figsize=(180, 90))
    fig.subplots_mm(ncols=1, gridspec_kw={
        'left': 10, 'right': 127.5, 'bottom': 12.5, 'top': 2.5})
    fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 72.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5, 'wspace': 15})
    subaxes = bowstr_utils.subsubplots(fig, fig.axes[:1])[0]

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=subaxes[9], loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], loc='sw')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[2], loc='sw')

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
        ax.text(
            1.08, 0.5,
            'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(fig.axes[0].bbox)
        ax.set_ylim(-2, 2)
        ax.set_yticks([-1, 1])
        ax.tick_params(labelleft=ax.get_subplotspec().is_last_row())

    # for each non-tide unit
    tide = pres.pop('tide')
    for i, unit in enumerate(pres):
        color = f'C{i}'
        ts = pres[unit]

        # plot (series.plot with deltas affected by #18910)
        ax = fig.axes[1]
        xcorr = crosscorr(ts, tide)
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
    fig.axes[1].set_xticks([-12, 0, 12])
    fig.axes[1].set_xlabel('time delay (h)')
    fig.axes[1].set_ylabel('cross-correlation', labelpad=0)
    fig.axes[1].set_ylim((-0.42, 0.42) if filt == 'deriv' else (-1.05, 1.05))
    fig.axes[1].yaxis.set_major_formatter(lambda y, pos: f'{y:g}'*(pos % 2))
    fig.axes[2].axvline(0.0, ls=':')
    fig.axes[2].set_xlim(0.5, 3.5)
    fig.axes[2].invert_yaxis()
    fig.axes[2].set_xlabel('phase delay (h)')
    fig.axes[2].set_ylabel('sensor depth (m)')

    # set labels and remove empty headlines in date tick labels
    subaxes[4].set_ylabel(
        'stress change (Pa/s)' if filt == 'deriv' else 'stress (kPa)')
    subaxes[9].set_xlabel('')
    subaxes[9].set_xticks(subaxes[9].get_xticks(), [
        label.get_text()[1:] for label in subaxes[9].get_xticklabels()])

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
    filters = ['12hbp', '12hhp', '24hbp', '24hhp', 'deriv', 'phase']
    plotter = bowstr_utils.MultiPlotter(plot, filters=filters)
    plotter()


if __name__ == '__main__':
    main()

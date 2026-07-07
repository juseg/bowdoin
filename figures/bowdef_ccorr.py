#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation cross-correlation."""

import numpy as np
import pandas as pd
import absplots as apl
import bowdef_gnssv  # FIXME move contents to bowdef_utils
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
    subaxes = bowstr_utils.subsubplots(fig, fig.axes[:1], nrows=8, sharey=False)[0]

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=subaxes[-1], loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], loc='sw')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[2], loc='sw')

    # plot borehole velocity
    df = bowdef_gnssv.read_gnss_velocities()
    # df.vh1.plot(ax=fig.axes[0], color='0.9')
    # df.vhs.plot(ax=fig.axes[0], color='tab:blue')

    # read strain rate
    # strain = read_gnss_strain_rate()
    # strain.plot(ax=axes[1])

    # highpass-filter stress series
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(filt=None, resample='10min', tide=True)
    tide = pres.pop('tide')
    pres = pres / 1e3

    # plot tilt rate (6h = 36*10min)
    tilx = bowstr_utils.load(variable='tilx').resample('10min').mean()
    tily = bowstr_utils.load(variable='tily').resample('10min').mean()
    tilx = tilx.interpolate(limit_area='inside', method='linear')
    tily = tily.interpolate(limit_area='inside', method='linear')
    kwargs = {'window_length': 72, 'polyorder': 2, 'delta': 1, 'deriv': 1}
    tilx = bowdef_gnssv.savgol_dataframe(tilx, **kwargs)
    tily = bowdef_gnssv.savgol_dataframe(tily, **kwargs)
    tilt = np.arccos(np.cos(tilx)*np.cos(tily)) * 180 / np.pi
    tilt = tilt[tilt.index >= '2014-07-17']
    tilt *= 3600 * 24 * 365.25 / pd.to_timedelta('10min').total_seconds()
    # tilt.plot(ax=fig.axes[0], legend=False)

    # prepare joined dataframe interpolated to tilt samples
    # FIXME rename to tilt or data
    if method == '10min':
        pres = tilt.join(
            df.vhs.resample('10min').interpolate(limit=2, method='linear'))

    # prepare joined dataframe using intersecting samples only
    elif method == 'inner':
        pres = tilt.join(df.vhs.groupby(level=0).mean(), how='inner')
        pres = pres.resample('30min').mean()

    # prepare joined dataframe interpolated to maximum sampling rate
    elif method == 'outer':
        pres = tilt.join(df.vhs.groupby(level=0).mean(), how='outer')
        pres = pres.resample('5min').mean().interpolate(
            limit=2, method='linear')

    # load stress data
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = pres['20150516':'20150815']
    pres = pres.dropna(how='all', axis=1)

    # plot time series
    for i, unit in enumerate(pres):
        ax = subaxes[i]
        color = 'tab:cyan' if unit == 'vhs' else f'C{i}'
        pres[unit].plot(ax=ax, color=color, legend=False)
        ax.text(
            1.08, 0.5,
            '\nSurface\nspeed\n'r'($m\,a^{-1}$)' if unit == 'vhs' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(fig.axes[0].bbox)
        ax.set_ylim((250, 650) if unit == 'vhs' else (2, 13))
        ax.set_yticks([300, 600] if unit == 'vhs' else [5, 10])
        ax.tick_params(labelleft=len(subaxes)-i in (1, 2))

    # for each non-tide unit
    # FIXME rename to vhs or gnss
    tide = pres.pop('vhs')
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
    # fig.axes[1].set_ylim((-0.42, 0.42) if filt == 'deriv' else (-1.05, 1.05))
    fig.axes[1].yaxis.set_major_formatter(lambda y, pos: f'{y:g}'*(pos % 2))
    fig.axes[2].axvline(0.0, ls=':')
    # fig.axes[2].set_xlim(0.5, 3.5)
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
    methods = ['10min', 'inner', 'outer']
    plotter = bowstr_utils.MultiPlotter(plot, methods=methods)
    plotter()


if __name__ == '__main__':
    main()

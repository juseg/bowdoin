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

def correlate_dataframes(df0, df1):
    """Compute cross-correlations between columns of two dataframes."""

    # FIXME allow shift_max argument as timedelta string
    shift_max = 36 / pd.to_timedelta(pd.infer_freq(df0.index)).total_seconds() * 3600

    # return concatenation of cross-correlations
    return pd.concat([crosscorr(
        df0[column], df1.get(column, df1.squeeze()),
        wmin=-shift_max, wmax=shift_max)
            for column in df0], axis=1)


def crosscorr(series, other, wmin=-72*1.5, wmax=72*1.5):
    """Return cross correlation for multiple lags."""
    shifts = np.arange(wmin, wmax+1)
    df = pd.DataFrame(
        data=[series.shift(i, freq='infer') for i in shifts],
        index=shifts*pd.to_timedelta(pd.infer_freq(series.index)))
    return df.corrwith(other, axis=1).rename(series.name)


def plot_correlations(ax0, ax1, depth, xcorr):
    """Plot cross-correlations and phase delays."""

    # for each non-tide unit
    for i, unit in enumerate(xcorr):
        color = f'C{i}'

        # plot (series.plot with deltas affected by #18910)
        ax0.plot(-xcorr.index.total_seconds()/3600, xcorr[unit])

        # find maximum correlation (a positive shift is a negative delay)
        shift = abs(xcorr[unit]).idxmax()
        delay = -shift.total_seconds()/3600
        ax0.plot(delay, xcorr[unit][shift], c=color, marker='o')

        # plot phase delays
        ax1.plot(delay, depth[unit], c=color, marker='o')
        ax1.text(delay+0.1, depth[unit]-1.0, unit, color=color, clip_on=True)

    # set axes properties
    ax0.axvline(0.0, ls=':')
    ax0.set_xticks(range(-36, 48, 12))
    ax0.set_xlabel('time delay (h)')
    ax0.set_ylabel('cross-correlation', labelpad=0)
    ax0.xaxis.set_major_formatter(lambda x, pos: f'{x:g}'*(pos % 2))
    ax0.yaxis.set_major_formatter(lambda y, pos: f'{y:g}'*(pos % 2))
    ax1.axvline(0.0, ls=':')
    ax1.invert_yaxis()
    ax1.set_xlabel('phase delay (h)')
    ax1.set_ylabel('sensor depth (m)')


def plot_time_series(ax, depth, df, var, ref):
    """Plot relevant time series on just as many subsubplots."""

    # initialize subsubplots
    subaxes = bowstr_utils.subsubplots(
        ax.figure, [ax], nrows=df[var].shape[1]+(df[ref].shape[1]==1),
        sharey=False)[0]

    # plot primary variable time series
    for i, unit in enumerate(df[var].columns):
        ax = subaxes[i]
        df[var, unit].plot(ax=ax, color=f'C{i}', legend=False)
        ax.text(
            1.08, 0.5, f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=f'C{i}',
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(ax.figure.axes[0].bbox)
        ax.set_ylim({'pres': (-20, 20), 'tilt': (2, 13)}[var])
        ax.set_yticks({'pres': (-10, 10), 'tilt': (5, 10)}[var])
        ax.tick_params(labelleft=len(subaxes)-i in (1, 2))

    # plot reference variable time series
    if ref != 'tilt':
        ax = subaxes[-1]
        df[ref].plot(ax=ax, color='tab:cyan', legend=False)
        ax.text(
            1.08, 0.5, {
                'gnss': '\nSurface\nspeed\n'r'($m\,a^{-1}$)',
                'tide': 'Pituffik\ntide'r'$\,/\,$10'}[ref], color='tab:cyan',
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(ax.figure.axes[0].bbox)
        ax.set_ylim({'gnss': (250, 560), 'tide': (-20, 20)}[ref])
        ax.set_yticks({'gnss': (300, 600), 'tide': (-10, 10)}[ref])

    # set labels and remove empty headlines in date tick labels
    subaxes[df[var].shape[1]//2].set_ylabel({
        'pres': 'stress (kPa)', 'tilt': r'tilt rate ($°\,a^{-1}$)'}[var])
    subaxes[-1].set_xlabel('')


def plot(couple='ti2sp', method='inner'):
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 90))
    fig.subplots_mm(ncols=1, gridspec_kw={
        'left': 10, 'right': 127.5, 'bottom': 12.5, 'top': 2.5})
    fig.subplots_mm(ncols=2, gridspec_kw={
        'left': 72.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5, 'wspace': 15})

    # add subfigure labels
    bowtem_utils.add_subfig_label('(a)', ax=fig.axes[0], loc='sw')
    bowtem_utils.add_subfig_label('(b)', ax=fig.axes[1], loc='sw')
    bowtem_utils.add_subfig_label('(c)', ax=fig.axes[2], loc='sw')

    # load all variables
    var = {'st': 'pres', 'tr': 'tilt'}[couple[:2]]
    ref = {'sp': 'gnss', 'ti': 'tide', 'tr': 'tilt'}[couple[3:]]
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join=method)
    # df = df.loc['20140701':'20140831']  # 2014 with gnss but before refreezing
    # df = df.loc['20140916':'20141016']  # 2014 all units but no gnss data
    df = df.loc['20150516':'20150815']  # 2015 full gnss record
    # df = df.loc['20150527':'20150608']  # 2015 spring tidal buildup
    # df = df.loc['20150704':'20150803']  # 2015 summer daily cycles
    # df = df.loc['20150723':'20150803']  # 2015 summer daily zoom
    # df = df.loc['20160601':'20160930']  # 2016 full gnss record
    # df = df.loc['20160701':'20160830']  # 2016 summer daily cycles
    # df = df.loc['20160901':'20160923']  # 2016 fall tidal cycles
    df = df.dropna(how='all', axis=1)

    # compute cross-correlations
    correlation = correlate_dataframes(df[var], df[ref])

    # plot time series
    plot_time_series(fig.axes[0], depth, df, var, ref)
    plot_correlations(fig.axes[1], fig.axes[2], depth, correlation)

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
    couples = ['st2sp', 'st2ti', 'st2tr', 'tr2sp', 'tr2ti']
    methods = ['inner', 'mixed', 'outer']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples, methods=methods)
    plotter()


if __name__ == '__main__':
    main()

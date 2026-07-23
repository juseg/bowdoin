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

def correlate_dataframes(df0, df1, smin='-36h', smax='36h'):
    """Compute cross-correlations between columns of two dataframes."""

    # convert min and max shifts to integer
    freq = pd.to_timedelta(pd.infer_freq(df0.index))
    smin = int(pd.to_timedelta(smin)/freq)
    smax = int(pd.to_timedelta(smax)/freq)

    # compute correlations and phase delays
    ccorr = pd.concat([
        correlate_series(df0[col], df1.get(col, df1.squeeze()), smin, smax)
        for col in df0], axis=1)
    delay = -abs(ccorr).idxmax()
    return ccorr, delay


def correlate_series(series, other, smin, smax):
    """Return cross correlation for multiple lags."""
    shifts = np.arange(smin, smax+1)
    data = (series.shift(i, freq='infer') for i in shifts)
    index = shifts*pd.to_timedelta(pd.infer_freq(series.index))
    df = pd.DataFrame(data=data, index=index)
    return df.corrwith(other, axis=1).rename(series.name)


def plot_correlations(ax, ccorr, delay):
    """Plot cross-correlations and phase delays."""

    # plot cross-correlation (series.plot with deltas affected by #18910)
    ax.plot(-ccorr.index/pd.to_timedelta('1h'), ccorr)
    for i, unit in enumerate(ccorr):
        ax.plot(
            delay[unit]/pd.to_timedelta('1h'), ccorr[unit][-delay[unit]],
            color=f'C{i}', marker='o')

    # set axes properties
    ax.axvline(0.0, ls=':')
    ax.set_xticks(range(-36, 48, 12))
    ax.set_xlabel('time delay (h)')
    ax.set_ylabel('cross-correlation', labelpad=0)
    ax.xaxis.set_major_formatter(lambda x, pos: f'{x:g}'*(pos % 2))
    ax.yaxis.set_major_formatter(lambda y, pos: f'{y:g}'*(pos % 2))


def plot_phase_delays(ax, depth, delay):
    """Plot cross-correlations and phase delays."""

    # plot phase delays
    delay = delay / pd.to_timedelta('1h')
    for i, unit in enumerate(delay.index):
        ax.plot(delay[unit], depth.get(unit, 0), color=f'C{i}', marker='o')
        ax.text(
            delay[unit], depth.get(unit, 0)-1, f' {unit.replace('vh', 'GNSS')}',
            color=f'C{i}')

    # set axes properties
    ax.axvline(0.0, ls=':')
    ax.invert_yaxis()
    ax.set_xlabel('phase delay (h)')
    ax.set_ylabel('sensor depth (m)')
    ax.set_xlim(ax.get_xlim()[0], 1.2*ax.get_xlim()[1]-0.2*ax.get_xlim()[0])

    # force axes limits on surface speed
    if 'vh' in delay:
        ax.set_ylim(103, -23)


def plot_time_series(ax, depth, df, var, ref):
    """Plot relevant time series on just as many subsubplots."""

    # initialize subsubplots
    subaxes = bowstr_utils.subsubplots(
        ax.figure, [ax], nrows=df[var].shape[1]+(df[ref].shape[1]==1),
        sharey=False)[0]

    # hardcoded axes properties
    ylabel = {'pres': 'stress (kPa)', 'tilt': r'tilt rate ($°\,a^{-1}$)'}
    ylim = {
        'gnss': (200, 700), 'pres': (-20, 20), 'tide': (-20, 20),
        'tilt': (2, 13)}
    yticks = {
        'gnss': (300, 600), 'pres': (-10, 10), 'tide': (-10, 10),
        'tilt': (5, 10)}
    ytext = {
        'gnss': '\nSurface\nspeed\n'r'($m\,a^{-1}$)',
        'tide': 'Pituffik\ntide'r'$\,/\,$10'}

    # plot primary variable time series
    for i, unit in enumerate(df[var].columns):
        ax = subaxes[i]
        df[var, unit].plot(ax=ax, color=f'C{i}', legend=False)
        ax.text(
            1.08, 0.5,
            ytext.get(var, f'{unit}\n{depth.get(unit, 0):.0f}'r'$\,$m'),
            color=f'C{i}', fontsize=6, fontweight='bold', rotation='vertical',
            ha='center', va='center', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(ax.figure.axes[0].bbox)
        ax.set_ylim(ylim.get(var, None))
        ax.set_yticks(yticks.get(var, ax.get_yticks()))
        ax.tick_params(labelleft=len(subaxes)-i in (1, 2))

    # plot reference variable time series
    if ref != 'tilt':
        ax = subaxes[-1]
        df[ref].plot(ax=ax, color='tab:cyan', legend=False)
        ax.text(
            1.08, 0.5, ytext.get(ref), color='tab:cyan',
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

        # set axes properties
        ax.get_lines()[0].set_clip_box(ax.figure.axes[0].bbox)
        ax.set_ylim(ylim.get(ref, None))
        ax.set_yticks(yticks.get(ref, ax.get_yticks()))

    # set labels and remove empty headlines in date tick labels
    subaxes[df[var].shape[1]//2].set_ylabel(ylabel.get(var))
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
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join=method)

    # select time interval and drop empty records
    # df = df.loc['20140701':'20140831']  # 2014 with gnss but before refreezing
    # df = df.loc['20140916':'20141016']  # 2014 all units but no gnss data
    # df = df.loc['20150527':'20150608']  # 2015 spring tidal buildup
    # df = df.loc['20150704':'20150803']  # 2015 summer daily cycles
    # df = df.loc['20150723':'20150803']  # 2015 summer daily zoom
    # df = df.loc['20160601':'20160930']  # 2016 full gnss record
    # df = df.loc['20160701':'20160830']  # 2016 summer daily cycles
    # df = df.loc['20160901':'20160923']  # 2016 fall tidal cycles
    df = df.loc['20150516':'20150815']  # 2015 full gnss record
    df = df.dropna(how='all', axis=1)

    # compute cross-correlations and phase delays
    var = {'sp': 'gnss', 'st': 'pres', 'tr': 'tilt'}[couple[:2]]
    ref = {'sp': 'gnss', 'ti': 'tide', 'tr': 'tilt'}[couple[3:]]
    ccorr, delay = correlate_dataframes(df[var], df[ref])

    # plot time series, correlations and phase delays
    plot_time_series(fig.axes[0], depth, df, var, ref)
    plot_correlations(fig.axes[1], ccorr, delay)
    plot_phase_delays(fig.axes[2], depth, delay)

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
    couples = ['sp2ti', 'st2sp', 'st2ti', 'st2tr', 'tr2sp', 'tr2ti']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples)
    plotter()


if __name__ == '__main__':
    main()

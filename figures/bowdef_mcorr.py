#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation moving window cross-correlation."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd

import bowdef_ccorr  # FIXME move contents to utils
import bowdef_utils
import bowstr_utils


def compute_rolling_correlation(series, other, window='14D', stride='7D'):
    """Compute rolling-window cross-correlation between two series."""

    # convert min and max shifts to integer
    smin = '-12h'
    smax = '12h'
    freq = pd.to_timedelta(pd.infer_freq(series.index))
    smin = int(pd.to_timedelta(smin)/freq)
    smax = int(pd.to_timedelta(smax)/freq)

    window = pd.to_timedelta(window)
    starts = pd.date_range(
        start=series.index[0], end=series.index[-1]-window, freq=stride)
    slices = [slice(start, start+window) for start in starts]
    corr = pd.DataFrame(
        data=[bowdef_ccorr.correlate_series(series[s], other[s], smin, smax) for s in slices],
        index=starts+window/2,
        ).transpose()
    return corr


def plot(couple='ti2sp', method='inner'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 10, 'right': 7.5, 'bottom': 10, 'top': 2.5})
    axes = bowstr_utils.subsubplots(fig, [ax], nrows=9)[0]
    cax = fig.add_axes_mm([100, 30, 60, 5])

    # load all variables
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join=method)

    # subset
    # df = df.drop(columns=['UI03', 'UI02'])
    # pres = pres['20140901':'20150901']  # first year looks good
    # tide = tide['20140901':'20150901']  # things get messy then

    # compute cross-correlations and phase delays
    var = {'sp': 'gnss', 'st': 'pres', 'tr': 'tilt'}[couple[:2]]
    ref = {'sp': 'gnss', 'ti': 'tide', 'tr': 'tilt'}[couple[3:]]

    # for each unit
    for i, unit in enumerate(df.tilt):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'
        series = df.tilt[unit].dropna()

        # plot cross correlation and zero contour
        tide = df.tide.squeeze().dropna()
        corr = compute_rolling_correlation(series, tide)
        print(series.shape, tide.shape, corr.shape)
        img = ax.imshow(
            corr, aspect='auto', cmap='Greys_r', vmin=-1, vmax=1, extent=(
                *mpl.dates.date2num((corr.columns[0], corr.columns[-1])),
                *-corr.index[[-1, 0]].total_seconds()/3600))
        ax.contour(
            mpl.dates.date2num(corr.columns),
            -corr.index.total_seconds()/3600,
            corr, colors=['0.25'], linestyles=['dashed'], levels=[0])

        # find maximum anticorrelation
        delay = -corr.dropna(axis=1, how='all').idxmin()
        delay = delay.dt.total_seconds()/3600
        delay = delay.where(corr.min() <= -0.5)
        delay = delay.resample('1D').nearest()  # for compat with mpl.dates
        delay.plot(ax=ax, drawstyle='steps-mid', color='w', lw=2, alpha=0.5)
        delay.plot(ax=ax, drawstyle='steps-mid', color=color)

        # add text label
        ax.text(
            1.02, 0.5, 'Pituffik\ntide'r'$\,/\,$10' if unit == 'tide' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

    # add colorbar
    cax.figure.colorbar(img, cax=cax, orientation='horizontal')
    cax.set_xlabel('cross-correlation with Pituffik tide / 10')

    # set axes properties
    ax.set_xlim('20140701', '20170801')
    ax.set_yticks([0, 3, 6])
    axes[len(axes)//2].set_ylabel('phase delay (h)')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    couples = ['sp2ti', 'st2sp', 'st2ti', 'st2tr', 'tr2sp', 'tr2ti']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples)
    plotter()


if __name__ == '__main__':
    main()

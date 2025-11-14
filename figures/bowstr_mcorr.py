#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress moving window cross-correlation."""

import absplots as apl
import matplotlib as mpl
import numpy as np
import pandas as pd

import bowstr_utils
import bowtem_utils


def crosscorr(series, other, wmin=-48, wmax=12):
    """Compute cross-correlation between two series."""
    shifts = np.arange(wmin, wmax+1)
    dataframe = pd.DataFrame(
        data=[series.shift(i, freq='infer') for i in shifts],
        index=pd.to_timedelta(shifts*series.index.freq))
    return dataframe.corrwith(other, axis=1)


def rollcorr(series, other, window='14D', stride='7D'):
    """Compute rolling-window cross-correlation between two series."""
    window = pd.to_timedelta(window)
    starts = pd.date_range(
        start=series.index[0], end=series.index[-1]-window, freq=stride)
    slices = [slice(start, start+window) for start in starts]
    corr = pd.DataFrame(
        data=[crosscorr(series[s], other[s]) for s in slices],
        index=starts+window/2,
        ).transpose()
    return corr


def plot(filt='24hhp'):
    """Plot and return full figure for given options."""

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 10, 'right': 7.5, 'bottom': 10, 'top': 2.5})
    axes = bowstr_utils.subsubplots(fig, [ax], nrows=7)[0]

    # load stress data
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(
        filt=filt, interp=True, resample='10min', tide=True)
    tide = pres.pop('tide')

    # subset
    pres = pres.drop(columns=['UI03', 'UI02'])
    # pres = pres['20140901':'20150901']  # first year looks good
    # tide = tide['20140901':'20150901']  # things get messy then

    # for each unit
    for i, unit in enumerate(pres):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'
        series = pres[unit].dropna()

        # plot cross correlation and zero contour
        corr = rollcorr(series, tide)
        ax.imshow(
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

    # set axes properties
    ax.set_xlim('20140701', '20170801')
    ax.set_yticks([0, 3, 6])
    axes[len(axes)//2].set_ylabel('phase delay (h)')

    # return figure
    return fig


def main():
    """Main program called during execution."""
    filters = ['12hbp', '12hhp', '24hbp', '24hhp', 'deriv']  # FIXME 'phase'
    plotter = bowstr_utils.MultiPlotter(plot, filters=filters)
    plotter()


if __name__ == '__main__':
    main()

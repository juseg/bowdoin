#!/usr/bin/env python
# Copyright (c) 2018-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation moving window cross-correlation."""

import absplots as apl
import matplotlib as mpl
import pandas as pd

import bowdef_ccorr  # FIXME move contents to utils
import bowdef_utils
import bowstr_utils


def correlate_rolling_dataframes(df0, df1, window='14D', stride='7D'):
    """Compute rolling-window cross-correlation between two dataframes."""

    # prepare rolling-window slicing
    index = df0.index
    window = pd.to_timedelta(window)
    starts = pd.date_range(start=index[0], end=index[-1]-window, freq=stride)
    slices = [slice(start, start+window) for start in starts]

    # compute rolling-window cross-correlation
    series = (
        bowdef_ccorr.correlate_dataframes(
            df0.loc[s], df1.loc[s], '-12h', '12h').transpose().stack()
        for s in slices)
    mcorr = pd.DataFrame(data=series, index=starts+window/2)
    return mcorr


def plot_rolling_correlations(ax, depth, mcorr):
    """Plot rolling-window cross-correlations and phase delays."""

    # initialize subsubplots
    units = mcorr.columns.levels[0]
    axes = [ax] if len(units) == 1 else bowstr_utils.subsubplots(
        ax.figure, [ax], nrows=len(units))[0]

    # for each unit
    for i, unit in enumerate(units):
        ax = axes[i]
        color = f'C{i+2*(i > 3)}'

        # plot cross correlation and zero contour
        corr = mcorr[unit].transpose()
        dates = mpl.dates.date2num(mcorr.index)
        shifts = -mcorr[unit].columns / pd.to_timedelta('1h')
        img = ax.imshow(
            mcorr[unit].transpose(), aspect='auto', cmap='Greys_r',
            vmin=-1, vmax=1, extent=(*dates[[0, -1]], *shifts[[-1, 0]]))
        ax.contour(
            dates, shifts, mcorr[unit].transpose(), colors=['0.25'],
            linestyles=['dashed'], levels=[0])

        # find maximum anticorrelation
        delay = -corr.dropna(axis=1, how='all').idxmin()
        delay = delay / pd.to_timedelta('1h')
        delay = delay.where(corr.min() <= -0.5)
        delay = delay.resample('1D').nearest()  # for compat with mpl.dates
        delay.plot(ax=ax, drawstyle='steps-mid', color='w', lw=2, alpha=0.5)
        delay.plot(ax=ax, drawstyle='steps-mid', color=color)

        # add text label
        ax.text(
            1.02, 0.5, r'surface speed ($m\,a^{-1}$)' if unit =='GNSS' else
            f'{unit}\n{depth[unit]:.0f}'r'$\,$m', color=color,
            fontsize=6, fontweight='bold', ha='center', va='center',
            rotation='vertical', transform=ax.transAxes)

    # set axes properties
    ax.set_xlim('20140701', '20170801')
    ax.set_yticks([0, 3, 6])
    axes[len(axes)//2].set_ylabel('phase delay (h)')

    # return last image for the colorbar
    return img


def plot_colorbar(cax, img, var, ref):
    """Plot colorbar with adapted text label."""

    # add colorbar
    labels = {
        'gnss': r'speed ($m\,a^{-1}$)',
        'pres': r'stress (kPa)',
        'tide': r'tide$\,/\,$10',
        'tilt': r'tilt rate ($°\,a^{-1}$)'}
    cax.figure.colorbar(img, cax=cax, orientation='horizontal')
    cax.set_xlabel(f'{labels[var]} vs {labels[ref]}')


def plot(couple='ti2sp', method='inner'):
    """Plot and return full figure for given options."""

    # correlation variables
    var = {'sp': 'gnss', 'st': 'pres', 'tr': 'tilt'}[couple[:2]]
    ref = {'sp': 'gnss', 'ti': 'tide', 'tr': 'tilt'}[couple[3:]]

    # initialize figure
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw={
        'left': 10, 'right': 7.5, 'bottom': 10+37.5*(var=='gnss'), 'top': 2.5})
    cax = fig.add_axes_mm([100, 30, 60, 5])

    # load all variables
    depth = bowstr_utils.load(variable='dept').iloc[0]
    df = bowdef_utils.load_multivariate(filt='24hbp', join=method)
    df = df.drop(columns=['UI03', 'UI02'], level=1)

    # compute rolling-window cross-correlations
    mcorr = correlate_rolling_dataframes(df[var], df[ref])

    # plot correlations and phase delays
    img = plot_rolling_correlations(ax, depth, mcorr)
    plot_colorbar(cax, img, var, ref)

    # return figure
    return fig


def main():
    """Main program called during execution."""
    couples = ['sp2ti', 'st2sp', 'st2ti', 'st2tr', 'tr2sp', 'tr2ti']
    plotter = bowstr_utils.MultiPlotter(plot, couples=couples)
    plotter()


if __name__ == '__main__':
    main()

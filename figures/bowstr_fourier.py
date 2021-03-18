#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress Fourier transforms."""

import numpy as np
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl
import util.str


def fourier(series):
    """Compute Fourier transform ready for plotting."""

    # interpolate, drop nans, and differentiate
    series = series.interpolate(limit_area='inside')
    series = series.dropna()
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]  # first value is nan after diff

    # prepare frequencies and periods
    frequency = np.fft.rfftfreq(series.shape[-1], 1)

    # compute real fft amplitude
    rfft = np.fft.rfft(series.values)
    amplitude = np.abs(rfft)

    # to compute spectral power or gain
    # power = amplitude**2
    # gain = 10*np.log10(power)

    # remove zero frequency, convert to periods
    period = (1/frequency[1:]) * (series.index.freq/pd.to_timedelta('1D'))
    amplitude = amplitude[1:]

    # return periods and amplitude
    return period, amplitude


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    axes = np.array([fig.subplots_mm(  # 40x25 mm panels
        nrows=3, ncols=4, sharex=True, sharey=True, gridspec_kw=dict(
            left=10, right=2.5, bottom=7.5, top=2.5, hspace=2.5, wspace=2.5)),
                     fig.subplots_mm(  # 20x10 mm panels
        nrows=3, ncols=4, sharex=True, sharey=True, gridspec_kw=dict(
            left=27.5, right=5, bottom=10, top=20, hspace=22.5, wspace=22.5))])

    # load pressure and freezing dates
    depth = util.str.load(variable='dept').iloc[0]
    pres = util.str.load().resample('1H').mean() * 1e3  # Pa
    date = util.str.load_freezing_dates()

    # for each tilt unit
    for i, unit in enumerate(pres):
        color = 'C{}'.format(i)

        # plot amplitude spectrum
        for ax in axes[:, :, :3].reshape(2, -1)[:, i]:
            ax.plot(*fourier(pres[unit][date[unit]:]), color=color)

        # add corner tag
        ax = axes[0, :, :3].flat[i]
        ax.text(0.95, 0.9, r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
                color=color, fontsize=6, fontweight='bold',
                transform=ax.transAxes, ha='right')

    # plot tide data
    tide = util.str.load_pituffik_tides().resample('1H').mean() * 1e2  # Pa/10
    for ax in axes[:, -1, -1]:
        ax.plot(*fourier(tide), c='C9')
        ax.set_xscale('log')
        ax.set_yscale('log')

    # add corner tag
    ax = axes[0, -1, -1]
    ax.text(0.95, 0.05, 'Pituffik\ntide'+r'$\,/\,$10', color='C9', fontsize=6,
            fontweight='bold', ha='right', transform=ax.transAxes)

    # move tide inset axes
    ax = axes[1, -1, -1]
    ax.set_position(ax.get_position().translated(0, 15/120))

    # annotate tidal modes
    kwargs = dict(arrowprops=dict(arrowstyle='-'), ha='center',
                  textcoords='offset points')
    ax.annotate(r'$S_2$', xy=(12.00/24, 1e3), xytext=(-12, 20), **kwargs)
    ax.annotate(r'$M_2$', xy=(12.42/24, 1e3), xytext=(+00, 20), **kwargs)
    ax.annotate(r'$N_2$', xy=(12.55/24, 1e3), xytext=(+12, 20), **kwargs)
    ax.annotate(r'$K_1$', xy=(23.93/24, 1e3), xytext=(-4, 20), **kwargs)
    ax.annotate(r'$O_1$', xy=(25.82/24, 1e3), xytext=(+4, 20), **kwargs)
    ax.text(16/24, 1e7, 'Tidal constituents', ha='center')

    # set (all) inset axes properties
    ax.set_xlim(0.4, 1.2)
    ax.set_ylim(10**-0.8, 10**3.4)
    ax.set_xticks([12/24, 12.42/24, 23.93/24, 25.82/24])
    ax.set_xticks([], minor=True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # set labels
    axes[0, 2, 2].get_xticklabels()[-1].set_color('r')
    axes[0, 2, 2].set_xlabel(
        '      period (days)      ', bbox=dict(ec='none', fc='w'),
        labelpad=-8, x=-1.25/40)
    axes[0, 0, 2].set_ylabel(('amplitude of stress change\n'
                              r'after refreezing ($Pa\,s^{-1}$)'), y=-1.25/35)
    axes[0, 0, 2].yaxis.set_label_position("right")

    # mark one inset
    mark_inset(*axes[:, 0, 0], loc1=1, loc2=3, ec='0.75', ls='--')

    # remove unused axes
    for ax in axes[:, :2, 3].flat:
        ax.set_visible(False)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

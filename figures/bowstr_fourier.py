#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress Fourier transforms."""

import numpy as np
import pandas as pd
import matplotlib as mpl
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


def subplots():
    """Prepare 2x10 subplots with optimized locations."""

    # initialize figure with 2x3x4 subplots grid
    fig = apl.figure_mm(figsize=(180, 120))
    axes = np.array([fig.subplots_mm(  # 40x35 mm panels
        nrows=3, ncols=4, sharex=True, sharey=True, gridspec_kw=dict(
            left=10, right=2.5, bottom=7.5, top=2.5, hspace=2.5, wspace=2.5)),
                     fig.subplots_mm(  # 20x10 mm panels
        nrows=3, ncols=4, sharex=True, sharey=False, gridspec_kw=dict(
            left=27.5, right=5, bottom=25, top=5, hspace=22.5, wspace=22.5))])

    # hide 2x2x1 unused axes in the top-right corner
    for ax in axes[:, :2, 3].flat:
        ax.set_visible(False)

    # reshape to 12x2 and delete invisible axes
    axes = axes.reshape(2, -1).T
    axes = np.delete(axes, [3, 7], 0)

    # set log scale on all axes
    for ax in axes.flat:
        ax.set_xscale('log')

    # mark all the insets
    for axespair in axes:
        mark_inset(*axespair, loc1=2, loc2=4, ec='0.75', ls='--')

    # set tidal ticks, no labels on insets
    for ax in axes[:, 1]:
        ax.set_xlim(0.4, 1.4)
        ax.set_xticks([12/24, 12.42/24, 23.93/24, 25.82/24])
        ax.set_xticks([], minor=True)
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    # move tide axes upwards
    for ax in axes[-1]:
        ax.set_position(ax.get_position().translated(0, 5/120))

    # set labels on last main axes
    ax = axes[-1, 0]
    ax.set_xlabel('xlabel', labelpad=7)
    ax.set_ylabel('ylabel', labelpad=0)
    ax.yaxis.label.set_position((10, 2+(3.75-5)/35))
    ax.yaxis.label.set_va('top')

    # annotate tidal modes on last inset axes
    ax = axes[-1, 1]
    blended = mpl.transforms.blended_transform_factory(
        ax.transData, ax.transAxes)
    kwargs = dict(ha='center', xycoords=blended, textcoords='offset points')
    ax.annotate('Tidal constituents', xy=(16/24, 1), xytext=(0, 36), **kwargs)
    kwargs.update(arrowprops=dict(arrowstyle='-'))
    ax.annotate(r'$S_2$', xy=(12.00/24, 1), xytext=(-12, 20), **kwargs)
    ax.annotate(r'$M_2$', xy=(12.42/24, 1), xytext=(+00, 20), **kwargs)
    ax.annotate(r'$N_2$', xy=(12.55/24, 1), xytext=(+12, 20), **kwargs)
    ax.annotate(r'$K_1$', xy=(23.93/24, 1), xytext=(-4, 20), **kwargs)
    ax.annotate(r'$O_1$', xy=(25.82/24, 1), xytext=(+4, 20), **kwargs)

    # return figure and axes
    return fig, axes


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = subplots()

    # load pressure and freezing dates
    depth = util.str.load(variable='dept').iloc[0]
    pres = util.str.load().resample('1H').mean()  # kPa
    date = util.str.load_freezing_dates()

    # for each tilt unit
    for i, unit in enumerate(pres):
        color = 'C{}'.format(i)

        # plot amplitude spectrum
        per, amp = fourier(pres[unit][date[unit]:])
        for ax in axes[i]:
            ax.plot(per, amp, color=color)

        # add main axes text label
        axes[i, 0].text(
            0.95, 0.35, r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
            color=color, fontsize=6, fontweight='bold',
            transform=axes[i, 0].transAxes, ha='right')

        # set inset axes limits
        axes[i, 1].set_ylim(np.array([-0.05, 1.05])*amp[per < 2].max())

    # plot tide data
    tide = util.str.load_pituffik_tides().resample('1H').mean() / 10  # kPa/10
    for ax in axes[-1]:
        ax.plot(*fourier(tide), c='C9')

    # add main axes corner tag
    axes[-1, 0].text(
        0.95, 0.1, r'Pituffik tide$\,/\,$10', color='C9', fontsize=6,
        fontweight='bold', ha='right', transform=axes[-1, 0].transAxes)

    # set inset axes limites
    axes[-1, 1].set_ylim(np.array([-0.05, 1.05])*amp[per < 2].max())

    # set labels
    axes[-1, 0].set_xlabel('period (days)')
    axes[-1, 0].set_ylabel(
        'amplitude of stress change\n'+r'after refreezing ($kPa\,s^{-1}$)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

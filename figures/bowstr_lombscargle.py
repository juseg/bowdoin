#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress Lomb-Scargle periodograms."""

import numpy as np
from scipy import signal

import util.str


def lombscargle(series, periods):
    """Compute Lomb-Scargle periodogram ready for plotting."""

    # interpolate, drop nans, and differentiate
    series = series.interpolate(limit_area='inside')
    series = series.dropna()
    series = series.diff() / series.index.to_series().diff().dt.total_seconds()
    series = series[1:]  # first value is nan after diff

    # prepare frequencies and periods
    frequency = 2 * np.pi / periods

    # compute periodogram
    time = (series.index-series.index[0]).total_seconds()
    power = signal.lombscargle(time, series, frequency)
    # amplitude = (4*power/len(periods))**0.5  # maybe

    # return spectral power
    return power


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = util.str.subplots_fourier()

    # load stress and freezing dates
    depth = util.str.load(variable='dept').iloc[0]
    pres = util.str.load() * 1e3  # kPa
    date = util.str.load_freezing_dates()

    # periods in days for main and inset axes (we need many points)
    periods = (np.logspace(-1, 3, 1001), np.logspace(-0.35, 0.1, 1001))

    # for each tilt unit
    for i, unit in enumerate(pres):
        color = 'C{}'.format(i)

        # subset series post-freezing
        series = pres[unit][date[unit]:]

        # plot periodograms
        for ax, days in zip(axes[i], periods):
            ax.plot(days, lombscargle(series, days*24*3600), color=color)

        # add main axes text label
        axes[i, 0].text(
            0.95, 0.35, r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
            color=color, fontsize=6, fontweight='bold',
            transform=axes[i, 0].transAxes, ha='right')

    # plot tide data
    series = util.str.load_pituffik_tides() / 10  # kPa / 10
    for ax, days in zip(axes[-1], periods):
        ax.plot(days, lombscargle(series, days*24*3600), color='C9')

    # add main axes corner tag
    axes[-1, 0].text(
        0.95, 0.1, r'Pituffik tide$\,/\,$10', color='C9', fontsize=6,
        fontweight='bold', ha='right', transform=ax.transAxes)

    # set labels
    axes[-1, 0].set_xlabel('period (days)')
    axes[-1, 0].set_ylabel(
        'Lomb-Scargle power\n'+r'after refreezing ($kPa^{2}\,s^{-2}$)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

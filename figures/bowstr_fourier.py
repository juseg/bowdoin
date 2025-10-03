#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin stress Fourier transforms."""

import numpy as np
import pandas as pd
import bowstr_utils


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
    fig, axes = bowstr_utils.subplots_fourier()

    # load stress and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load().resample('1h').mean()  # kPa
    date = bowstr_utils.load_freezing_dates()

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
    tide = bowstr_utils.load_pituffik_tides().resample('1h').mean() / 10  # kPa/10
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

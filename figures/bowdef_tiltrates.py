#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt rates."""

import absplots as apl

import bowdef_utils
import bowstr_utils


def plot_faded(ax, df, dates):
    """Plot dataframe columns with faded records before given dates."""
    for i, (unit, series) in enumerate(df.items()):
        series[:dates[unit]].plot(
            ax=ax, alpha=0.25, color=f'C{i}', label='_nolegend_')
        series[dates[unit]:].plot(ax=ax, color=f'C{i}')


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        figsize=(180, 90), nrows=2, sharex=True, gridspec_kw={
            'left': 15, 'right': 2.5, 'bottom': 10, 'top': 2.5, 'hspace': 2.5})

    # load tilt rate, temperature and freezing dates
    tilt = bowdef_utils.load_tilt_rates(method='kernel', window='3h')
    temp = bowstr_utils.load(variable='temp').resample('1h').mean()
    dates = bowstr_utils.load_freezing_dates()

    # plot tilt rate and temperature
    plot_faded(axes[0], tilt, dates)
    plot_faded(axes[1], temp, dates)

    # set axes properties
    axes[0].legend(loc='upper right', ncols=2)
    axes[0].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[1].set_ylabel('temperature (°C)')
    axes[1].set_xlabel('')
    axes[0].set_xlim('20140701', '20170801')
    axes[0].set_ylim(-1, 21)
    axes[1].set_ylim(-6.5, 0.5)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin deformation tilt rates."""

import absplots as apl
import matplotlib as mpl

import bowdef_utils
import bowstr_utils
import bowtem_utils


def plot_faded(ax, df, dates):
    """Plot dataframe columns with faded records before given dates."""
    for i, (unit, series) in enumerate(df.items()):
        series[:dates[unit]].plot(
            ax=ax, alpha=0.25, color=f'C{i}', label='_nolegend_')
        series[dates[unit]:].plot(ax=ax, color=f'C{i}')


def mark_zoom(ax, zoom):
    """Indicate zoom on main axes and connect it to zoom axes below."""
    indicator = ax.indicate_inset_zoom(zoom, edgecolor='0.75', alpha=1)
    for connector in indicator.connectors:
        connector.set_visible(False)
    for x, corner in zip(zoom.get_xlim(), (0, 1)):
        ax.figure.add_artist(mpl.patches.ConnectionPatch(
            xyA=(x, 0), coordsA=ax.get_xaxis_transform(),
            xyB=(corner, 1), coordsB=zoom.transAxes, color='0.75'))


def main():
    """Main program called during execution."""

    # initialize figure with tilt rate, summer zooms and temperature axes
    fig = apl.figure_mm(figsize=(180, 150))
    axes = [
        fig.add_axes_mm([15, 102.5, 162.5, 45]),
        fig.add_axes_mm([15, 57.5, 77.5, 35]),
        fig.add_axes_mm([100, 57.5, 77.5, 35]),
        fig.add_axes_mm([15, 10, 162.5, 37.5])]
    bowtem_utils.add_subfig_labels(
        axes, bbox={'alpha': 0.85, 'ec': 'none', 'fc': 'w'})

    # load tilt rate, temperature and freezing dates
    tilt = bowdef_utils.load_tilt_rates(method='kernel', window='3h')
    temp = bowstr_utils.load(variable='temp').resample('1h').mean()
    dates = bowstr_utils.load_freezing_dates()

    # plot tilt rate and temperature
    plot_faded(axes[0], tilt, dates)
    plot_faded(axes[3], temp, dates)

    # plot summer zooms
    for ax, year in zip(axes[1:3], [2015, 2016]):
        tilt.plot(ax=ax, legend=False, xlabel='')
        ax.set_xlim(f'{year}0601', f'{year}0901')
        ax.set_ylim(-1, 21)
        mark_zoom(axes[0], ax)

    # set axes properties
    axes[3].legend(loc='upper right', ncols=5)
    axes[0].set_ylabel(r'tilt rate ($°\,a^{-1}$)')
    axes[3].set_ylabel('temperature (°C)')
    axes[0].set_xlabel('')
    axes[3].set_xlabel('')
    axes[0].set_xlim('20140701', '20170801')
    axes[3].set_xlim('20140701', '20170801')
    axes[0].set_ylim(-1, 21)
    axes[2].tick_params(labelleft=False)
    axes[3].set_ylim(-6.5, 0.5)

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

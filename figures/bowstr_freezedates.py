#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides temperature time series."""

import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates
import brokenaxes as bax
import absplots as apl
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    spec = fig.add_gridspec_mm(
        ncols=1, nrows=2,
        left=12.5, right=2.5, bottom=12.5, top=2.5, hspace=2.5)
    axes = [bax.brokenaxes(
        despine=False, width_ratios=[1, 3], wspace=0.02,
        subplot_spec=subspec, tilt=75,
        xlims=(pd.to_datetime(('20140708', '20140908')),
               pd.to_datetime(('20140908', '20171216')))) for subspec in spec]

    # add subfigure labels
    bowtem_utils.add_subfig_labels([ax.axs[0] for ax in axes])

    # load stress, temperature and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(variable='wlev').resample('1h').mean() / 1e3
    temp = bowstr_utils.load(variable='temp').resample('1h').mean()
    date = bowstr_utils.load_freezing_dates()

    # plot stress and temperature
    # data.plot(ax=ax, legend=False)  # fails (#40)
    for ax, data in zip(axes, (pres, temp)):
        ax.plot(data.index, data.values)

        # for each unit
        for i, unit in enumerate(pres):
            color = 'C{}'.format(i)

            # and freezing date
            ax.plot(
                date[unit], data[unit][date[unit]], color=color, marker='o')
            ax.axvline(date[unit], color=color, lw=0.5)

            # add unit label
            last = data[unit].dropna().tail(1)
            ax.annotate(
                r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
                color='C{}'.format(i), fontsize=6, fontweight='bold',
                xy=(last.index[0], last.iloc[0]), xytext=(4, 0),
                textcoords='offset points', ha='left', va='center')

    # add campaigns (only on large format plot)
    bowtem_utils.add_field_campaigns(ax=axes[0].axs[0], ytext=-1)
    bowtem_utils.add_field_campaigns(ax=axes[0].axs[1], ytext=-1)
    bowtem_utils.add_field_campaigns(ax=axes[1].axs[0], ytext=0.02)
    bowtem_utils.add_field_campaigns(ax=axes[1].axs[1], ytext=0.02)

    # set axes properties
    axes[1].set_ylim(-6.5, 0.5)
    axes[0].set_ylabel('stress (MPa)', labelpad=24)
    axes[1].set_ylabel('temperature (°C)', labelpad=24)

    # fix pandas-style date ticks
    for ax in axes:

        # better ticks on left axes (workaround #40)
        locator = mpl.dates.MonthLocator()
        formatter = mpl.dates.ConciseDateFormatter(
            locator, formats=['%b\n%Y', '%b']+['']*4, show_offset=False)
        ax.axs[0].xaxis.set_major_locator(locator)
        ax.axs[0].xaxis.set_major_formatter(formatter)
        ax.axs[0].xaxis.set_minor_locator(mdates.AutoDateLocator())

        # better ticks on left axes (workaround #40)
        locator = mpl.dates.MonthLocator([1, 7])
        formatter = mpl.dates.ConciseDateFormatter(
            locator, formats=['%b\n%Y', '%b']+['']*4, show_offset=False)
        ax.axs[1].xaxis.set_major_locator(locator)
        ax.axs[1].xaxis.set_major_formatter(formatter)
        ax.axs[1].xaxis.set_minor_locator(mdates.MonthLocator())

    # no tick labels on top axes
    axes[0].set_xticklabels([])

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

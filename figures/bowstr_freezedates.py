#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides temperature time series."""

import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates
import absplots as apl
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, axes = apl.subplots_mm(
        ncols=2, nrows=2, figsize=(180, 120), sharex='col', sharey='row',
        gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 2.5, 'wspace': 1, 'width_ratios': [1, 3]})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(axes[:, 0])

    # load stress, temperature and freezing dates
    depth = bowstr_utils.load(variable='dept').iloc[0]
    pres = bowstr_utils.load(variable='wlev').resample('1h').mean() / 1e3
    temp = bowstr_utils.load(variable='temp').resample('1h').mean()
    date = bowstr_utils.load_freezing_dates()

    # plot stress and temperature
    # data.plot(ax=ax, legend=False)  # fails (#40)
    for ax in axes.flat:
        data = pres if ax.get_subplotspec().is_first_row() else temp
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
    bowtem_utils.add_field_campaigns(ax=axes[0, 0], ytext=-1)
    bowtem_utils.add_field_campaigns(ax=axes[0, 1], ytext=-1)
    bowtem_utils.add_field_campaigns(ax=axes[1, 0], ytext=0.02)
    bowtem_utils.add_field_campaigns(ax=axes[1, 1], ytext=0.02)

    # set axes properties
    axes[0, 0].set_ylabel('stress (MPa)')
    axes[1, 0].set_ylabel('temperature (°C)')
    axes[0, 0].set_xlim(pd.to_datetime(('20140708', '20140908')))
    axes[0, 1].set_xlim(pd.to_datetime(('20140908', '20171216')))
    axes[1, 0].set_ylim(-6.5, 0.5)

    # emulate broken axes
    for ax in axes.flat:
        gs = ax.get_subplotspec()
        ax.spines['left'].set_visible(gs.is_first_col())
        ax.spines['right'].set_visible(gs.is_last_col())
        ax.tick_params(labelbottom=True, left=gs.is_first_col())
        ax.plot(
            [1*gs.is_first_col()]*2, [0, 1], clip_on=False, ls='',
            marker=[(-1, -2), (1, 2)], mec='k', ms=6, transform=ax.transAxes)

    # fix pandas-style date ticks
    for row in axes:

        # better ticks on left axes (workaround #40)
        locator = mpl.dates.MonthLocator()
        formatter = mpl.dates.ConciseDateFormatter(
            locator, formats=['%b\n%Y', '%b']+['']*4, show_offset=False)
        row[0].xaxis.set_major_locator(locator)
        row[0].xaxis.set_major_formatter(formatter)
        row[0].xaxis.set_minor_locator(mdates.AutoDateLocator())

        # better ticks on left axes (workaround #40)
        locator = mpl.dates.MonthLocator([1, 7])
        formatter = mpl.dates.ConciseDateFormatter(
            locator, formats=['%b\n%Y', '%b']+['']*4, show_offset=False)
        row[1].xaxis.set_major_locator(locator)
        row[1].xaxis.set_major_formatter(formatter)
        row[1].xaxis.set_minor_locator(mdates.MonthLocator())

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

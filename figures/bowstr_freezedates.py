#!/usr/bin/env python
# Copyright (c) 2019-2021, Julien Seguinot (juseg.github.io)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides temperature time series."""

import pandas as pd
import matplotlib as mpl
import matplotlib.dates as mdates
import brokenaxes as bax
import absplots as apl
import util.str


def main():
    """Main program called during execution."""

    # initialize figure
    fig = apl.figure_mm(figsize=(85, 60))
    gridspec_kw = dict(left=12.5, right=2.5, bottom=12.5, top=2.5)
    subplotspec = fig.add_gridspec_mm(nrows=1, ncols=1, **gridspec_kw)[:]
    ax = bax.brokenaxes(
        despine=False, width_ratios=[1, 3], wspace=0.02,
        subplot_spec=subplotspec, tilt=75,
        xlims=(pd.to_datetime(('20140708', '20140908')),
               pd.to_datetime(('20140908', '20170908'))))

    # load temperature and freezing dates
    temp = util.str.load(variable='temp').resample('1H').mean()
    date = util.str.load_freezing_dates()

    # plot temperature and freezing dates
    # temp.plot(ax=ax, legend=False)  # fails (#40)
    ax.plot(temp.index, temp.values)
    ax.plot(date, [ts.loc[date[unit]] for unit, ts in temp.items()], 'k+')

    # add campaigns (only on large format plot)
    # util.com.plot_field_campaigns(ax=ax.axs[0], ytext=0.01)
    # util.com.plot_field_campaigns(ax=ax.axs[1], ytext=0.01)

    # set axes properties
    ax.set_ylim(-6.5, 0.5)
    ax.set_ylabel('temperature (°C)', labelpad=24)

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

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

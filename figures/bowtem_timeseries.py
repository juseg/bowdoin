#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature time series."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import brokenaxes as bax
import absplots as apl
import util

# Pandas plot methods do not work on brokenaxes (issue #40)
pd.plotting.register_matplotlib_converters()


def format_date_axis(axis):
    """
    Locate ticks and format date labels on a time axis.
    """
    locator = mdates.MonthLocator([1, 4, 7, 10])
    formatter = mdates.ConciseDateFormatter(
        locator, formats=['%b\n%Y', '%b']+['']*4, show_offset=False)
    axis.set_major_locator(locator)
    axis.set_minor_locator(mdates.MonthLocator())
    axis.set_major_formatter(formatter)


def main():
    """Main program called during execution."""

    # FIXME implement gridspec_mm in absplots
    # fig = apl.figure_mm(figsize=(180, 120))
    # subplotspec = fig.add_gridspec_mm(1, 1)[:]

    # initialize figure
    gridspec_kw = dict(left=12.5, right=2.5, bottom=12.5, top=2.5)
    fig, ax = apl.subplots_mm(figsize=(180, 120), gridspec_kw=gridspec_kw)
    subplotspec = ax.get_subplotspec()
    ax.remove()
    ax = bax.brokenaxes(despine=False, height_ratios=[4, 1], hspace=0.02,
                        subplot_spec=subplotspec, tilt=15,
                        ylims=[(-15.5, -6.5), (-6.5, 0.5)])

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # plot daily means
        temp, _, _ = util.tem.load_all(bh)
        temp = temp.resample('1D').mean()
        ax.plot(temp.index, temp.values, c=color, lw=0.5)
        # temp.plot(ax=ax, c=color, legend=False, lw=0.5)  # fails (issue #40)

        # plot manual readings
        if bh != 'bh1':
            manu, mask = util.tem.load_manual(bh)
            manu = manu.resample('1D').mean()
            mask = mask.resample('1D').prod()
            ax.plot(manu.where(mask).index, manu.where(mask).values,
                    c='none', marker='o', mec=color)
            ax.plot(manu.mask(mask).index, manu.mask(mask).values,
                    c=color, marker='o')
            # manu.where(mask).plot(ax=ax, c='none', marker='o', mec=color)
            # manu.mask(mask).plot(ax=ax, c=color, marker='o')  # fails (#40)

        # add profile dates
        for date in util.tem.PROFILES_DATES[bh]:
            ax.axvline(date, color=color, ls='--')

    # add campaigns
    util.com.plot_field_campaigns(ax=ax.axs[0], ytext=-1)
    util.com.plot_field_campaigns(ax=ax.axs[1])

    # set axes properties
    ax.set_ylabel(u'temperature (°C)', labelpad=24)
    ax.set_xlim('20140615', '20170815')

    # set better ticks (pandas would do it if #40 is fixed)
    format_date_axis(ax.axs[0].xaxis)
    format_date_axis(ax.axs[1].xaxis)
    ax.axs[0].xaxis.set_tick_params(which='both', length=0)
    ax.axs[0].set_yticks(range(-6, 1))
    ax.axs[1].set_yticks(range(-14, -6, 2))

    # add standalone legend
    ax.axs[0].legend(*zip(*[
        (plt.Line2D([], [], c=c, marker='o'*(bh != 'bh1')),
         bh.upper()) for bh, c in util.tem.COLOURS.items()]))

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()

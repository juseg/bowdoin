#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature time series."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import brokenaxes as bax
import absplots as apl
import bowtem_utils
import util.com

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

    # initialize figure
    fig = apl.figure_mm(figsize=(180, 120))
    gridspec_kw = dict(left=12.5, right=2.5, bottom=12.5, top=2.5)
    subplotspec = fig.add_gridspec_mm(nrows=1, ncols=1, **gridspec_kw)[:]
    ax = bax.brokenaxes(despine=False, height_ratios=[4, 1], hspace=0.02,
                        subplot_spec=subplotspec, tilt=15,
                        ylims=[(-15.5, -6.5), (-6.5, 0.5)])

    # for each borehole
    for bh, color in bowtem_utils.COLOURS.items():

        # plot daily means
        temp, depth, _ = bowtem_utils.load_all(bh)
        temp = temp.resample('1D').mean()
        ax.plot(temp.index, temp.values, c=color)
        # temp.plot(ax=ax, c=color, legend=False)  # fails (issue #40)

        # plot manual readings
        if bh != 'bh1':
            manu, mask = bowtem_utils.load_manual(bh)

            # for bh2 draw dotted line across 2016 data gap
            if bh == 'bh2':
                ax.plot(manu[:3].index, manu[:3], c=color, ls=':', lw=0.5)
                # manu[1:3].plot(ax=ax, c=color, ls=':', lw=0.5)  # fails (#40)

            # for all boreholes draw filled and empty markers
            manu = manu.resample('1D').mean()
            mask = mask.resample('1D').prod() > 0
            ax.plot(manu.where(mask).index, manu.where(mask).values,
                    c='none', marker='o', mec=color)
            ax.plot(manu.mask(mask).index, manu.mask(mask).values,
                    c=color, marker='o')
            # manu.where(mask).plot(ax=ax, c='none', marker='o', mec=color)
            # manu.mask(mask).plot(ax=ax, c=color, marker='o')  # fails (#40)

        # add profile dates
        for date in bowtem_utils.PROFILES_DATES[bh]:
            offset = (0 if bh in ('bh1', 'bh3') else 3)
            ax.axvline(date, color=color, ls=(offset, [2, 4]))

        # add unit labels
        offsets = dict(
            LT01=8, LT02=2, LT03=-2, LT04=-5, LT05=2, LT06=3, LT07=-3, LT09=-1,
            LT10=3, LT11=-2, LT12=-2, LT13=-2, UP=-2, UT01=2, UT04=2, UT07=4,
            UT08=-4, UT09=0, UT10=-8, UT11=6, UT12=0, UT13=-2, UT14=-2)
        for unit in temp:
            last = temp[unit].dropna().tail(1)
            ax.annotate(
                r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
                color=color, clip_on=True, fontsize=6, fontweight='bold',
                xy=(last.index, last.iloc[0]),
                xytext=(6, offsets.get(unit, 0)),
                textcoords='offset points', ha='left', va='center')


    # add campaigns
    util.com.plot_field_campaigns(ax=ax.axs[0], ytext=-1)
    util.com.plot_field_campaigns(ax=ax.axs[1])

    # set axes properties
    ax.set_ylabel(u'temperature (°C)', labelpad=24)
    ax.set_xlim('20140615', '20171215')

    # set better ticks (pandas would do it if #40 is fixed)
    format_date_axis(ax.axs[0].xaxis)
    format_date_axis(ax.axs[1].xaxis)
    ax.axs[0].xaxis.set_tick_params(which='both', length=0)
    ax.axs[0].set_yticks(range(-6, 1))
    ax.axs[1].set_yticks(range(-14, -6, 2))

    # add standalone legend
    ax.axs[0].legend(*zip(*[
        (plt.Line2D([], [], c=c, marker='o'*(bh != 'bh1')),
         bh.upper()) for bh, c in bowtem_utils.COLOURS.items()]))

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

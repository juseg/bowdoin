#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature time series."""

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import absplots as apl
import bowtem_utils

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
    fig, axes = apl.subplots_mm(
        nrows=2, figsize=(180, 120), sharex=True, gridspec_kw={
            'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
            'hspace': 1, 'height_ratios': [4, 1]})

    # for each borehole
    for bh, color in bowtem_utils.COLOURS.items():

        # plot daily means
        temp, depth, _ = bowtem_utils.load_all(bh)
        temp = temp.resample('1D').mean()
        for ax in axes:
            ax.plot(temp.index, temp.values, c=color)
        # temp.plot(ax=ax, c=color, legend=False)  # fails (issue #40)

        # plot manual readings
        if bh != 'bh1':
            manu, mask = bowtem_utils.load_manual(bh)

            # for bh2 draw dotted line across 2016 data gap
            if bh == 'bh2':
                for ax in axes:
                    ax.plot(manu[:3].index, manu[:3], c=color, ls=':', lw=0.5)
                # manu[1:3].plot(ax=ax, c=color, ls=':', lw=0.5)  # fails (#40)

            # for all boreholes draw filled and empty markers
            manu = manu.resample('1D').mean()
            mask = mask.resample('1D').prod() > 0
            for ax in axes:
                ax.plot(manu.where(mask).index, manu.where(mask).values,
                        c='none', marker='o', mec=color)
                ax.plot(manu.mask(mask).index, manu.mask(mask).values,
                        c=color, marker='o')
            # manu.where(mask).plot(ax=ax, c='none', marker='o', mec=color)
            # manu.mask(mask).plot(ax=ax, c=color, marker='o')  # fails (#40)

        # add profile dates
        for date in bowtem_utils.PROFILES_DATES[bh]:
            offset = (0 if bh in ('bh1', 'bh3') else 3)
            for ax in axes:
                ax.axvline(date, color=color, ls=(offset, [2, 4]))

        # add unit labels
        offsets = dict(
            LT01=8, LT02=2, LT03=-2, LT04=-5, LT05=2, LT06=3, LT07=-3, LT09=-1,
            LT10=3, LT11=-2, LT12=-2, LT13=-2, UP=-2, UT01=2, UT04=2, UT07=4,
            UT08=-4, UT09=0, UT10=-8, UT11=6, UT12=0, UT13=-2, UT14=-2)
        for unit in temp:
            last = temp[unit].dropna().tail(1)
            for ax in axes:
                ax.annotate(
                    r'{}, {:.0f}$\,$m'.format(unit, depth[unit]),
                    color=color, clip_on=True, fontsize=6, fontweight='bold',
                    xy=(last.index, last.iloc[0]),
                    xytext=(6, offsets.get(unit, 0)),
                    textcoords='offset points', ha='left', va='center')


    # add campaigns
    bowtem_utils.add_field_campaigns(ax=axes[0])
    bowtem_utils.add_field_campaigns(ax=axes[1], ytext=0.05)

    # set axes properties
    axes[0].set_ylabel('temperature (°C)', y=3/8)
    axes[0].set_xlim('20140615', '20171215')
    axes[0].set_ylim(-6.5, 0.5)
    axes[1].set_ylim(-15.5, -6.5)

    # emulate broken axes
    for ax in axes.flat:
        gs = ax.get_subplotspec()
        ax.spines['top'].set_visible(gs.is_first_row())
        ax.spines['bottom'].set_visible(gs.is_last_row())
        ax.tick_params(labelleft=True, bottom=gs.is_last_row())
        ax.plot(
            [0, 1], [1*gs.is_last_row()]*2, clip_on=False, ls='',
            marker=[(-2, -1), (2, 1)], mec='k', ms=6, transform=ax.transAxes)

    # set better ticks (pandas would do it if #40 is fixed)
    format_date_axis(axes[0].xaxis)
    format_date_axis(axes[1].xaxis)
    axes[0].xaxis.set_tick_params(which='both', length=0)
    axes[0].set_yticks(range(-6, 1))
    axes[1].set_yticks(range(-14, -6, 2))

    # add standalone legend
    axes[0].legend(*zip(*[
        (plt.Line2D([], [], c=c, marker='o'*(bh != 'bh1')),
         bh.upper()) for bh, c in bowtem_utils.COLOURS.items()]))

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature time series."""

import matplotlib.pyplot as plt
import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    gridspec_kw = dict(left=12.5, right=2.5, bottom=12.5, top=2.5)
    fig, ax = apl.subplots_mm(figsize=(180, 90), gridspec_kw=gridspec_kw)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # plot daily means
        temp, _, _ = util.tem.load_all(bh)
        temp = temp.resample('1D').mean()
        temp.plot(ax=ax, c=color, legend=False, lw=0.5)

        # plot manual readings
        if bh != 'bh1':
            manu, mask = util.tem.load_manual(bh)
            manu = manu.resample('1D').mean()
            mask = mask.resample('1D').prod()
            manu.where(mask).plot(ax=ax, c='none', marker='o', mec=color)
            manu.mask(mask).plot(ax=ax, c=color, marker='o')

        # add profile dates
        for date in util.tem.PROFILES_DATES[bh]:
            ax.axvline(date, color=color, ls='--')

    # add campaigns
    util.com.plot_field_campaigns(ax=ax)

    # set axes properties
    ax.set_ylabel(u'temperature (°C)')
    ax.set_xlim('20140615', '20170815')
    ax.set_ylim(-14.5, 0.5)

    # add standalone legend
    ax.legend(*zip(*[(plt.Line2D([], [], c=c, marker='o'*(bh != 'bh1')),
                      bh.upper()) for bh, c in util.tem.COLOURS.items()]))

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature time series."""

import absplots as apl
import util


def main():
    """Main program called during execution."""

    # initialize figure
    gridspec_kw = dict(left=10, right=2.5, bottom=10, top=2.5)
    fig, ax = apl.subplots_mm(figsize=(150, 75), gridspec_kw=gridspec_kw)

    # for each borehole
    for bh, color in util.tem.COLOURS.items():

        # plot daily means
        temp, _, _ = util.tem.load_all(bh)
        temp = temp.resample('1D').mean()
        temp.plot(ax=ax, c=color, legend=False, lw=0.5)

        # add closure dates (see markers issue #14958)
        state = util.tem.estimate_closure_state(bh, temp)
        state.plot(x='date', y='temp', ax=ax, c=color, marker='+', ls='',
                   label=bh.upper())

        # add profile dates
        for date in util.tem.PROFILES_DATES[bh]:
            ax.axvline(date, color=color, ls='--')

    # add campaigns
    util.com.plot_field_campaigns(ax=ax)

    # set axes properties
    ax.set_ylabel(u'temperature (°C)')
    ax.set_xlim('20140615', '20170815')
    ax.set_ylim(-14.5, 0.5)

    # fix the legend (see markers issue #14958)
    ax.legend(*zip(*[(h, l) for h, l in zip(*ax.get_legend_handles_labels())
                     if l in ('BH1', 'BH2', 'BH3', 'ERR')]))

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()

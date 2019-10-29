#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util
import absplots as apl


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=2, gridspec_kw=dict(
        left=12.5, right=2.5, bottom=12.5, top=2.5, wspace=12.5))

    # load Thule and Bowdoin tide data
    thul = util.tid.load_pituffik_tides(start='2015-07', end='2015-08')
    bowd = util.tid.load_bowdoin_tides()

    # crop Thule data and downsample Bowdoin
    thul = thul[bowd.index[0]:bowd.index[-1]]
    bowd = bowd.reindex_like(thul, method='nearest')

    # plot time series
    ax = grid[0]
    thul.plot(ax=ax, label='Pituffik tide')
    bowd.plot(ax=ax, label='Bowdoin tide')
    ax.set_xlabel('Date', labelpad=-8.0)
    ax.set_ylabel('Tide (kPa)', labelpad=0.0)
    ax.legend()

    # plot scatter plot
    ax = grid[1]
    ax.scatter(thul, bowd, marker='+', alpha=0.25)
    ax.set_xlabel('Pituffik tide (kPa)')
    ax.set_ylabel('Bowdoin tide (kPa)', labelpad=0.0)

    # save
    util.com.savefig(fig)

    ## save alternative frames
    #util.com.savefig(fig, suffix='_z1')
    #ax.set_visible(False)
    #util.com.savefig(fig, suffix='_z0')


if __name__ == '__main__':
    main()

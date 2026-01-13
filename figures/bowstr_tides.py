#!/usr/bin/env python
# Copyright (c) 2019-2026, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides in fjord and Pituffik."""

import absplots as apl
import bowtem_utils
import bowstr_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 90), ncols=2, gridspec_kw={
        'left': 12.5, 'right': 2.5, 'bottom': 12.5, 'top': 2.5,
        'wspace': 12.5})
    bowtem_utils.add_subfig_labels(grid)

    # load Thule and Bowdoin tide data
    thul = bowstr_utils.load_pituffik_tides(start='2015-07', end='2015-08')
    bowd = bowstr_utils.load_bowdoin_tides()

    # plot time series
    ax = grid[0]
    thul.resample('10min').mean().plot(ax=ax, label='Pituffik tide')
    bowd.resample('10min').mean().plot(ax=ax, label='Bowdoin tide')
    ax.set_xlabel('')
    ax.set_ylabel('Tide (kPa)', labelpad=0.0)
    ax.set_xlim(bowd.index[[0, -1]].date)
    ax.set_xlim(bowd.index[0].floor('D'), bowd.index[-1].ceil('D'))
    ax.legend()

    # crop Thule data and downsample Bowdoin
    thul = thul[bowd.index[0]:bowd.index[-1]]
    bowd = bowd.reindex_like(thul, method='nearest')

    # plot scatter plot
    ax = grid[1]
    ax.scatter(thul, bowd, marker='+', alpha=0.25)
    ax.set_xlabel('Pituffik tide (kPa)')
    ax.set_ylabel('Bowdoin tide (kPa)', labelpad=0.0)

    # save
    fig.savefig(__file__[:-3])

    # save alternative frames  # FIXME formalise presentation mode
    # fig.savefig(__file__[:-3]+'_z1')
    # ax.set_visible(False)
    # fig.savefig(__file__[:-3]+'_z0')


if __name__ == '__main__':
    main()

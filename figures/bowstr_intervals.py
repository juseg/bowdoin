#!/usr/bin/env python
# Copyright (c) 2019-2025, Julien Seguinot (juseg.dev)
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin tides time intervals time series."""

from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import absplots as apl
import bowstr_utils
import bowtem_utils


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(
        figsize=(180, 90), nrows=9, ncols=2, sharex='col', sharey=True,
        gridspec_kw={
            'left': 12.5, 'right': 2.5, 'wspace': 12.5, 'bottom': 12.5,
            'top': 2.5, 'hspace': 2.5})

    # add subfigure labels
    bowtem_utils.add_subfig_labels(grid)

    # for each tilt unit
    pres = bowstr_utils.load()
    for i, unit in enumerate(pres):
        color = f'C{i}'

        # extract time steps
        step = pres[unit].dropna()
        step = step.index.to_series().diff().dt.total_seconds()/3600.0
        step = step[1:].resample('1h').mean()  # resample to get nice date axis

        # plot
        for ax in grid[i]:
            step.plot(ax=ax, c=color)

        # add corner tag
        grid[i, 0].text(0.9, 0.2, unit, color=color,
                        transform=grid[i, 0].transAxes)
        grid[i, 0].set_yticks([0, 2])
        grid[i, 0].set_ylim(-0.5, 2.5)

        # set up zoom
        grid[i, 1].set_xlim('20141101', '20141201')
        mark_inset(grid[i, 0], grid[i, 1], loc1=2, loc2=3, ec='0.5', ls='--')

    # set y label
    grid[4, 0].set_ylabel('time step (h)')

    # save
    fig.savefig(__file__[:-3])


if __name__ == '__main__':
    main()

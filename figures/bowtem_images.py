#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

"""Plot Bowdoin temperature profiles."""

import matplotlib.pyplot as plt
import absplots as apl
import util


def annotate_borehole(x, y, bh, ax=None, **kwargs):
    """Annotate a borehole with an empty circle."""
    ax = ax or plt.gca()
    color = util.tem.COLOURS[bh]
    ax.plot(x, y, color='none', marker='o', ms=6, mec=color)
    ax.text(x, y-50, bh.upper(), color=color, fontweight='bold', va='bottom',
            **kwargs)


def main():
    """Main program called during execution."""

    # initialize figure
    fig, grid = apl.subplots_mm(figsize=(180, 65), ncols=2, gridspec_kw=dict(
        left=2.5, right=2.5, bottom=2.5, top=5, wspace=2.5))

    # add subfigure labels
    for ax, label in zip(grid, 'ab'):
        util.com.add_subfig_label(ax=ax, text='('+label+')', c='w', ypad=10)
        ax.set_xticks([])
        ax.set_yticks([])

    # show lower site ground photo
    ax = grid[0]
    ax.set_title('Lower drilling site, 20160719')
    ax.imshow(plt.imread('../photos/julien-xt10-160719-145819-dev.jpg'))

    # mark glacier names
    ax.text(650, 350, 'Bowdoin Glacier', color='w', ha='center')
    ax.text(1550, 350, 'Obelisk G.', color='w', ha='center')

    # annotate borehole
    annotate_borehole(950, 762, 'bh3', ax=ax, ha='center')

    # show boreholes aerial photo
    ax = grid[1]
    ax.set_title('Aerial view, 20160721')
    ax.imshow(plt.imread('../photos/julien-xt10-160721-121549-dev.jpg'))

    # mark glacier name
    ax.text(1250, 100, 'Bowdoin Glacier', color='w', ha='center')

    # plot borehole positions
    annotate_borehole(497, 504, 'bh3', ax=ax, ha='center')
    annotate_borehole(1078, 422, 'bh2', ax=ax, ha='left')
    annotate_borehole(1065, 416, 'bh1', ax=ax, ha='right')

    # save
    util.com.savefig(fig)


if __name__ == '__main__':
    main()

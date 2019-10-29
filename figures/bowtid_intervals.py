#!/usr/bin/env python
# Copyright (c) 2019, Julien Seguinot <seguinot@vaw.baug.ethz.ch>
# Creative Commons Attribution-ShareAlike 4.0 International License
# (CC BY-SA 4.0, http://creativecommons.org/licenses/by-sa/4.0/)

import util as ut
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=9, ncols=2,
                              sharex='col', sharey=True, wspace=2.5, hspace=2.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
for i, u in enumerate(p):
    c = 'C%d' % i

    # extract time steps
    ts = p[u].dropna()
    ts = ts.index.to_series().diff().dt.total_seconds()/3600.0
    ts = ts[1:].resample('1H').mean()  # resample to get a nice date axis

    # plot
    for ax in grid[i]:
        ts.plot(ax=ax, c=c)

    # add corner tag
    grid[i, 0].text(0.95, 0.2, u, color=c, transform=grid[i, 0].transAxes)
    grid[i, 0].set_yticks([0, 2])
    grid[i, 0].set_ylim(-0.5, 2.5)

    # set up zoom
    x0, x1 = ['20141101', '20141201']
    grid[i, 1].set_xlim(x0, x1)
    mark_inset(grid[i, 0], grid[i, 1], loc1=2, loc2=3, ec='0.5', ls='--')

# set y label
grid[4, 0].set_ylabel('time step (h)')

# save
ut.pl.savefig(fig)

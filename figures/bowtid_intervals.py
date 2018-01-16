#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(85.0, 65.0), nrows=9, ncols=1,
                              sharex=True, sharey=True, hspace=1.5, wspace=1.5,
                              left=12.0, right=1.5, bottom=9.0, top=1.5)

# for each tilt unit
p = ut.io.load_bowtid_data('wlev')
for i, u in enumerate(p):
    ax = grid.flat[i]
    c = 'C%d' % i

    # extract time steps
    ts = p[u].dropna()
    ts[1:] = (ts.index[1:]-ts.index[:-1]).total_seconds()/3600.0
    ts = ts[1:].resample('1H').mean()  # resample to get a nice date axis

    # plot
    ts.plot(ax=ax, c=c)

    # add corner tag
    ax.text(0.95, 0.2, u, color=c, transform=ax.transAxes)
    ax.set_yticks([0, 2])
    ax.set_ylim(-0.5, 2.5)

# set y label
grid[4].set_ylabel('time step (h)')

# save
ut.pl.savefig(fig)

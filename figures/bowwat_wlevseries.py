#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=2, ncols=1,
                              sharex=True, sharey=False, wspace=2.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# load pressure data
hw = ut.io.load_data('pressure', 'wlev', 'both').resample('1D').mean()
hw = hw.mask(hw < 0.0)  # FIXME move to preprocessing
hi = ut.io.load_data('pressure', 'depth', 'both').resample('1D').mean().interpolate()

# plot pressure head and ice thickness
ax = grid[0]
hw.plot(ax=ax)
hi.plot(ax=ax, c='k', ls='--', lw=0.25, legend=False)

# set axes properties
ax.set_ylim(190.0, 260.0)
ax.set_ylabel('pressure head (m)')


# plot water pressure ratio
ax = grid[1]
rw = (hw/hi/0.910)
rw.plot(ax=ax, legend=False)
ax.axhline(1.0, c='k', ls='--', lw=0.25)

# add label
ax.set_ylim(0.75, 1.25)
ax.set_ylabel('ratio to overburden')

# save
ut.pl.savefig(fig)

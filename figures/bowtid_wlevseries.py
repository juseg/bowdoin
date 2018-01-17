#!/usr/bin/env python2
# coding: utf-8

import util as ut
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=2,
                              sharex=False, sharey=False, wspace=7.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# plot tilt unit water level
p = ut.io.load_bowtid_data('wlev').resample('1H').mean()
for ax in grid:
    p.plot(ax=ax, legend=False)

# add label
grid[0].set_ylabel('pressure head (m w.e.)')
grid[0].legend(ncol=3)

# zooming windows
zooms = dict(
    z1 = ['20140715', '20141015', 030.0, 390.0],  # zoom on closure phase
    z2 = ['20140901', '20141001', 120.0, 160.0],  # 12-h cycle U5, U4, U3, L4
    z3 = ['20150101', '20150201', 155.0, 185.0],  # 12-h cycle U5, U4
    z4 = ['20150901', '20151015', 160.0, 170.0],  # 12-h cycle U5
    z5 = ['20150915', '20151115', 205.0, 235.0],  # 14-day mode U4, L3
    z6 = ['20170315', '20170501', 135.0, 150.0],)  # 14-day mode U5

## save without right panel
#grid[1].set_visible(False)
#ut.pl.savefig(fig, suffix='_z0')
#grid[1].set_visible(True)

# mark zoom inset
mark_inset(grid[0], grid[1], loc1=2, loc2=3, ec='0.5', ls='--')

## save different zooms
#for k, v in zooms.iteritems():
#    grid[1].set_xlim(*v[:2])
#    grid[1].set_ylim(*v[2:])
#    ut.pl.savefig(fig, suffix='_'+k)

# save default
grid[1].set_xlim(*zooms['z2'][:2])
grid[1].set_ylim(*zooms['z2'][2:])
ut.pl.savefig(fig)

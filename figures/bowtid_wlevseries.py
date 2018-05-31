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
p = ut.io.load_bowtid_data('wlev').resample('1H').mean()/1e3
for ax in grid:
    p.plot(ax=ax, legend=False)

# add label
grid[0].set_ylabel('pressure (MPa)')
grid[0].legend(ncol=3)

# zooming windows
zooms = dict(
    z1 = ['20140715', '20141015', 0.25, 3.85],  # zoom on closure phase
    z2 = ['20140901', '20141001', 1.15, 1.55],  # 12-h cycle U5, U4, U3, L4
    z3 = ['20150101', '20150201', 1.55, 1.80],  # 12-h cycle U5, U4
    z4 = ['20150901', '20151015', 1.55, 1.65],  # 12-h cycle U5
    z5 = ['20150915', '20151115', 2.00, 2.30],  # 14-day mode U4, L3
    z6 = ['20170315', '20170501', 1.35, 1.45],)  # 14-day mode U5

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

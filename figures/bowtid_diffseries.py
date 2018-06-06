#!/usr/bin/env python2
# coding: utf-8

import util as ut
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import mark_inset

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=2,
                              sharex=False, sharey=True, wspace=7.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# plot tilt unit water level
p = ut.io.load_bowtid_data('wlev').resample('1H').mean()
p = p.diff()[1:]/3.6 + 9 - range(p.shape[1])  # Pa s-1
for ax in grid:
    p.plot(ax=ax, legend=False)

# plot tide data
z = ut.io.load_tide_data()['20140715':'20170715'].diff()[1:]
z.plot(ax=grid[1], c='k', label='Tide')

# set axes properties
grid[0].set_ylim(-1.0, 10.0)
grid[0].set_ylabel('pressure change ($Pa\,s^{-1}$)')
grid[0].legend(ncol=2, loc='lower right')

# zooming windows
zooms = dict(
    z1 = ['20140901', '20141001'],  # zoom with all sensors, L3 not frozen
    z2 = ['20140910', '20140915'],  # zoom on phase, L3 not frozen
    z3 = ['20141120', '20141125'],  # zoom phase, U2 and U2 lost
    z4 = ['20150101', '20150201'],  # zoom on 14-day modulation, 2 cycles
    z5 = ['20150901', '20151101'],  # zoom on 14-day modulation, 4 cycles
    z6 = ['20150601', '20150715'])  # zoom on summer, more complicated

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
grid[1].set_xlim(*zooms['z1'])
ut.pl.savefig(fig)

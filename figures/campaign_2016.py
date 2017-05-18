#!/usr/bin/env python2
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import util as ut

start = '2016-06-05'
end = '2016-07-21'

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)
bh = 'upstream'

# plot water pressure
c = ut.palette['darkblue']
ts = ut.io.load_data('pressure', 'wlev', 'downstream')[start:end].resample('1H').mean()
ts.plot(ax=ax, c=c, legend=False)

# add label and legend
ax.axhline(0.0, c='k', lw=0.5)
ax.set_ylabel(bh + ' water level (m)', color=c)
ax.set_ylim(227.0, 237.0)
ax.grid(axis='x', which='minor', ls=':', lw=0.1)

# plot upstream deformation velocity
ax = ax.twinx()
c = ut.palette['darkred']

# load data
exz = ut.io.load_strain_rate(bh, '2H')[start:end]
depth = ut.io.load_depth('tiltunit', bh).squeeze()
depth_base = ut.io.load_depth('pressure', bh).squeeze()

# ignore two lowest units on upstream borehole
broken = ['unit02', 'unit03']
depth.drop(broken, inplace=True)
exz.drop(broken, axis='columns', inplace=True)

# fit to a Glen's law
n, A = ut.al.glenfit(depth, exz.T)

# calc deformation velocity
vdef = ut.al.vsia(0.0, depth_base, n, A)
vdef = pd.Series(index=exz.index, data=vdef)

# plot
vdef.plot(ax=ax, c=c)

# set labels
ax.set_ylabel(bh + ' deformation velocity ($m\,a^{-1}$)', color=c)
ax.set_ylim(-20.0, 80.0)
ax.set_xlim(start, end)

# save
ut.pl.savefig(fig)

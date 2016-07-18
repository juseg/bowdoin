#!/usr/bin/env python2
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import util as ut

start = '2014-07-15'
end = '2014-08-01'

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)

# plot water level
bh = 'downstream'
c = ut.colors[bh]

# plot pressure sensor water level
ts = ut.io.load_data('pressure', 'wlev', bh)[start:end].resample('1H').mean()
ts.plot(ax=ax, c=c, legend=False)

# add label and legend
ax.set_ylabel('water level (m)', color=c)
ax.set_ylim(205.0, 255.0)

# plot upstream deformation velocity
ax = ax.twinx()
bh = 'upstream'
c = ut.colors[bh]

# load data
exz = ut.io.load_strain_rate(bh, '1H')[start:end]
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
ax.set_ylabel(r'deformation velocity ($m\,a^{-1}$)', color=c)
ax.set_ylim(-50.0, 250.0)
ax.set_xlim(start, end)

# save
fig.savefig('summer_2014')

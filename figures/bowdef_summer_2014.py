#!/usr/bin/env python2
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import bowdef_utils

start = '2014-07-15'
end = '2014-09-01'

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)

# plot ice cap air temp
c = '0.25'
ts = bowdef_utils.load_temp_sigma()[start:end].resample('3h').mean()
ts.plot(ax=ax, c=c, legend=False)

# add label and legend
ax.axhline(0.0, c='k', lw=0.5)
ax.set_ylabel(u'Qaanaaq ice cap air temp. (°C)', color=c)
ax.set_ylim(-10.0, 40.0)

# plot upper deformation velocity
ax = ax.twinx()
bh = 'upper'
c = bowdef_utils.colors[bh]

# load data
exz = bowdef_utils.load_strain_rate(bh, '3h')[start:end]
depth = bowdef_utils.load_depth('tiltunit', bh).squeeze()
depth_base = bowdef_utils.load_depth('pressure', bh).squeeze()

# ignore two lowest units on upper borehole
broken = ['UI01', 'UI02', 'UI03']
depth.drop(broken, inplace=True)
exz.drop(broken, axis='columns', inplace=True)

# fit to a Glen's law
n, A = bowdef_utils.glenfit(depth, exz.T)

# calc deformation velocity
vdef = bowdef_utils.vsia(0.0, depth_base, n, A)
vdef = pd.Series(index=exz.index, data=vdef)

# plot
vdef.plot(ax=ax, c=c)

# set labels
ax.set_ylabel(r'deformation velocity ($m\,a^{-1}$)', color=c)
ax.set_ylim(-20.0, 80.0)
ax.set_xlim(start, end)

# save
bowdef_utils.savefig(fig)

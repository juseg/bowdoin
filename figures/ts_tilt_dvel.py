#!/usr/bin/env python2
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[i]

    # load data
    exz = ut.io.load_strain_rate(bh, '1D')
    depth = ut.io.load_depth('tiltunit', bh).squeeze()
    depth_base = ut.io.load_depth('pressure', bh).squeeze()

    # ignore two lowest units on upstream borehole
    if bh == 'upstream':
        broken = ['unit02', 'unit03']
        depth.drop(broken, inplace=True)
        exz.drop(broken, axis='columns', inplace=True)

    # fit to a Glen's law
    n, A = ut.tilt.glenfit(depth, exz.T)

    # calc deformation velocity
    vdef = ut.tilt.vsia(0.0, depth_base, n, A)
    vdef = pd.Series(index=exz.index, data=vdef)

    # plot
    vdef.plot(ax=ax, c=c, label=bh)

# set labels
ax.set_ylabel(r'deformation velocity ($m\,a^{-1}$)')
ax.set_ylim(20.0, 60.0)
ax.legend()

# save
fig.savefig('ts_tilt_dvel')

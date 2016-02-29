#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[i]

    # read tilt unit tilt
    tilt = ut.io.load_strain_rate(bh, '1D', as_angle=True)

    # plot
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel(r'tilt angle velocity ' + bh + ' ($^{\circ}\,a^{-1}$)')
    ax.set_ylim(0.0, 15.0)

# save
fig.savefig('ts_tilt_avel')

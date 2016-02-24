#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[i]

    # read tilt unit tilt
    d0 = '2015-04-01'
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh).resample('1D')
    tilty = ut.io.load_data('tiltunit', 'tilty', bh).resample('1D')

    # compute tilt velocity
    dt = 1.0/365
    exz_x = np.sin(tiltx).diff()
    exz_y = np.sin(tilty).diff()
    exz = np.sqrt(exz_x**2+exz_y**2)
    tilt = np.arcsin(exz)*180/np.pi/dt

    # plot
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel(r'tilt angle velocity ' + bh + ' ($^{\circ}\,a^{-1}$)')
    ax.set_ylim(0.0, 15.0)

# save
fig.savefig('ts_tilt_avel')
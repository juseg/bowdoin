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
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh).resample('1H')
    tilty = ut.io.load_data('tiltunit', 'tilty', bh).resample('1H')

    # compute tilt velocity
    dt = 1.0/24/365
    tilt = np.arcsin(np.sqrt((np.sin(tiltx).diff()[1:])**2+
                             (np.sin(tilty).diff()[1:])**2))*180/np.pi/dt

    # plot
    ut.pl.rolling_plot(ax, tilt.iloc[:, -1], 24*1, c=c)

    # set title
    ax.set_ylabel(r'tilt velocity ' + bh + ' ($^{\circ}\,a^{-1}$)')
    ax.set_ylim(0.0, 15.0)

# save
fig.savefig('ts_tilt_avel')

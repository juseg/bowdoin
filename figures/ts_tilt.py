#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import matplotlib.pyplot as plt
import util as ut

refdate = '2014-11-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[i]

    # plot tilt unit temperature
    tiltx = ut.io.load_data('tiltunit', 'tiltx', bh)
    tilty = ut.io.load_data('tiltunit', 'tilty', bh)

    # compute reference values
    tx0 = tiltx[refdate].mean()
    ty0 = tilty[refdate].mean()

    # compute tilt relative to reference
    tilt = np.arcsin(np.sqrt((np.sin(tiltx)-np.sin(tx0))**2+
                             (np.sin(tilty)-np.sin(ty0))**2))*180/np.pi
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel('tilt ' + bh)

# save
fig.savefig('ts_tilt')

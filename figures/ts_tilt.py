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

    # plot tilt unit temperature
    df = ut.io.load_data('tiltunit', 'tilt', bh)
    df.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel('tilt ' + bh)

# save
fig.savefig('ts_tilt')

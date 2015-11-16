#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import projectglobals as gl

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(gl.boreholes):
    ax = grid[i]
    c = gl.colors[i]

    # plot tilt unit temperature
    df = gl.load_data('tiltunit', 'tilt', bh)
    df.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel('tilt ' + bh)

# save
fig.savefig('ts_tilt')

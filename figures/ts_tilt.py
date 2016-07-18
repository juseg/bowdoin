#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

refdate = '2014-11-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[1-i]
    c = ut.colors[bh]

    # plot tilt angle
    tilt = ut.io.load_total_strain(bh, refdate, as_angle=True)[refdate:]
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel('tilt ' + bh)

# save
fig.savefig('ts_tilt')

#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

refdate = '2014-11-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True, sharey=True)
grid[0].set_title('tilt angle ($^{\circ}$)')

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[bh]

    # plot tilt angle
    tilt = ut.io.load_total_strain(bh, refdate, as_angle=True).resample('1D').mean()
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.axvspan('2014-06-01', refdate, ec='none', fc='0.9')
    ax.set_xlim('2014-07-01', '2017-08-01')
    ax.set_ylabel(bh)

# save
ut.pl.savefig(fig)

#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import bowdef_utils

refdate = '2014-11-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True, sharey=True)
grid[0].set_title('tilt angle ($^{\circ}$)')

# for each borehole
for i, bh in enumerate(bowdef_utils.boreholes):
    ax = grid[i]
    c = bowdef_utils.colors[bh]

    # plot tilt angle
    tilt = bowdef_utils.load_total_strain(bh, refdate, as_angle=True).resample('1D').mean()
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.axvspan('2014-06-01', refdate, ec='none', fc='0.9')
    ax.set_xlim('2014-07-01', '2017-08-01')
    ax.set_ylabel(bh)

# save
bowdef_utils.savefig(fig)

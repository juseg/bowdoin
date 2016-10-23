#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

refdate = '2014-11-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True, sharey=True)
grid[0].set_title('tilt angle velocity ($^{\circ}\,a^{-1}$)')

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[bh]

    # read tilt unit tilt
    tilt = ut.io.load_strain_rate(bh, '1D', as_angle=True)  #[refdate:]

    # plot
    tilt.plot(ax=ax, c=c, legend=False)

    # set title
    ax.axvspan('2014-06-01', refdate, ec='none', fc='0.9')
    ax.set_xlim('2014-06-01', '2016-09-01')
    ax.set_ylabel(bh)
    ax.set_ylim(0.0, 15.0)

# save
fig.savefig('ts_tilt_avel')

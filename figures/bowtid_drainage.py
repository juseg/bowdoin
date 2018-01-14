#!/usr/bin/env python2
# coding: utf-8

import pandas as pd
import matplotlib.pyplot as plt
import util as ut

start = '2016-06-13'
end = '2016-06-15'

# initialize figure
fig, ax = plt.subplots(1, 1, sharex=True)

# plot water level
bh = 'lower'
c = ut.colors[bh]

# plot pressure sensor water level
ts = ut.io.load_data('pressure', 'wlev', bh)[start:end].resample('1H').mean()
ts.plot(ax=ax, c=c, legend=False)

# add label and legend
ax.set_ylabel('water level (m)', color=c)
ax.set_ylim(200.0, 225.0)

# plot upper angular velocities
ax = ax.twinx()
bh = 'upper'
c = ut.colors[bh]

# read tilt unit tilt
tilt = ut.io.load_strain_rate(bh, '1H', as_angle=True)[start:end]

# plot
tilt.plot(ax=ax, c=c, legend=False)

# set labels
ax.set_ylabel(r'deformation velocity ($m\,a^{-1}$)', color=c)
ax.set_ylim(0.0, 50.0)
ax.set_xlim(start, end)

# save
ut.pl.savefig(fig)

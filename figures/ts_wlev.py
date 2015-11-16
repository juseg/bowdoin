#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, ax = plt.subplots(1, 1)

# for each borehole
lines = []
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[i]

    # plot lowest tilt unit water level
    ts = ut.io.load_data('tiltunit', 'wlev', bh).resample('30T').iloc[:,0]
    ts.plot(ax=ax, c='0.75', legend=False)

    # plot pressure sensor water level
    ts = ut.io.load_data('pressure', 'wlev', bh).resample('30T')
    ts = ts.iloc[2:]  # remove the first hour corresponding to drilling
    ts.plot(ax=ax, c=ut.colors[i], legend=False)
    lines.append(ax.get_lines()[-1])  # select last line for the legend

# add label and legend
ax.set_ylabel('water level (m)')
ax.legend(lines, ut.boreholes)

# save
fig.savefig('ts_wlev')

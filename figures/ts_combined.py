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

# add twin axes
ax = ax.twinx()

# plot GPS velocity
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')
ut.pl.rolling_plot(ax, ts, 4*6, c=ut.colors[2])

# add label and set limits
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)', labelpad=0.0)
ax.set_xlim('2014-07-17', '2015-07-20')

# save
fig.savefig('ts_combined')

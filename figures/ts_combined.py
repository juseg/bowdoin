#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import projectglobals as gl

# initialize figure
fig, ax = plt.subplots(1, 1)

# for each borehole
lines = []
for i, bh in enumerate(gl.boreholes):
    c = gl.colors[i]

    # plot lowest tilt unit water level
    ts = gl.load_data('tiltunit', 'wlev', bh).resample('30T').iloc[:,0]
    ts.plot(ax=ax, c='0.75', legend=False)

    # plot pressure sensor water level
    ts = gl.load_data('pressure', 'wlev', bh).resample('30T')
    ts = ts.iloc[2:]  # remove the first hour corresponding to drilling
    ts.plot(ax=ax, c=gl.colors[i], legend=False)
    lines.append(ax.get_lines()[-1])  # select last line for the legend

# add label and legend
ax.set_ylabel('water level (m)')
ax.legend(lines, gl.boreholes)

# add twin axes
ax = ax.twinx()

# plot GPS velocity
ts = gl.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')
gl.rollplot(ax, ts, 4*3, c='g')

# add label and set limits
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')
ax.set_xlim('2014-07-17', '2015-07-20')

# save
fig.savefig('ts_combined')

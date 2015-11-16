#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import projectglobals as gl


# initialize figure
fig, grid = plt.subplots(4, 1, sharex=True)

# remove spines and compact plot
gl.unframe(grid[0], ['top', 'right'])
gl.unframe(grid[1], ['left'])
gl.unframe(grid[2], ['right'])
gl.unframe(grid[3], ['bottom', 'left'])
fig.subplots_adjust(hspace=0.0)

# plot GPS velocity
df = gl.load_data('dgps', 'velocity', 'upstream')
gl.rollplot(grid[0], df['vh'], 4*3, c='g')

# for each borehole
lines = [None, None]
for i, bh in enumerate(gl.boreholes):

    # plot pressure sensor water level
    df = gl.load_data('pressure', 'wlev', bh).resample('30T')
    df = df[2:]  # remove the first hour corresponding to drilling
    df.plot(ax=grid[1], c=gl.colors[i], lw=2.0, legend=False)
    lines[i] = grid[1].get_lines()[-1]  # select last line for the legend

    # plot tilt unit water level
    df = gl.load_data('tiltunit', 'wlev', bh)
    df.plot(ax=grid[1], c='k', alpha=0.2, legend=False)

    # plot tilt
    df = gl.load_data('tiltunit', 'tilt', bh).resample('180T')
    df.plot(ax=grid[2], c=gl.colors[i], lw=0.1, legend=False)

    # plot temperature
    df = gl.load_data('thstring', 'temp', bh).resample('180T')
    df = df[df.columns[(df.max() < 1.0)]]  # remove records above ice surface
    df.plot(ax=grid[3], c=gl.colors[i], lw=0.1, legend=False)
    df = gl.load_data('tiltunit', 'temp', bh).resample('180T')
    df.plot(ax=grid[3], c=gl.colors[i], lw=0.1, legend=False)

# add legend
grid[0].legend(lines, gl.boreholes)

# set labels
grid[0].set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')
grid[1].set_ylabel('water level (m)')
grid[2].set_ylabel(u'tilt (°)')
grid[3].set_ylabel(u'temperature (°C)')

# set axes limits
grid[0].set_ylim(200, 800)
grid[1].set_ylim(150, 250)
#grid[2].set_ylim(-10, 0)
grid[3].set_ylim(-10, 0)
grid[3].set_xlim('2014-07-17', '2015-07-20')

# save
fig.savefig('timeseries')

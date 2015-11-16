#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import projectglobals as gl


def get_pressure_wlev(bh):
    """Get water level from pressure sensor in a dataframe."""
    df = gl.load_data('pressure', 'wlev', bh)
    df = df['wlev'].resample('30T')  # resample and fill with nan
    return df[2:]  # remove the first hour corresponding to drilling


def get_tiltunit_wlev(bh):
    """Get water level from tilt sensor units in a dataframe."""
    df = gl.load_data('tiltunit', 'wlev', bh)
    return df


def get_tempsens_temp(bh):
    """Get temperature from temperature sensors in a dataframe."""
    df = gl.load_data('thstring', 'temp', bh)
    df = df.resample('180T')  # resample and fill with nan
    df = df[df.columns[(df.max() < 1.0)]]  # remove records above ice surface
    return df


def get_tiltunit_temp(bh):
    """Get temperature from tilt sensor units in a dataframe."""
    df = gl.load_data('tiltunit', 'temp', bh)
    df = df.resample('180T')  # resample and fill with nan
    return df


def get_tiltunit_tilt(bh):
    """Get tilt angle from tilt sensor units in a dataframe."""
    df = gl.load_data('tiltunit', 'tilt', bh)
    df = df.resample('180T')  # resample and fill with nan
    return df


def get_gps_velocity(method='backward'):
    """Get UTM 19 GPS velocity components in a dataframe."""
    df = gl.load_data('dgps', 'velocity', 'upstream')
    return df


# interval to match tilt unit pressure against water level from bottom
wlev_calib_intervals = [['2014-07-18', '2014-07-22'],
                        ['2014-07-29', '2014-08-02']]

# initialize figure
fig, grid = plt.subplots(4, 1, sharex=True)

# remove spines and compact plot
gl.unframe(grid[0], ['top', 'right'])
gl.unframe(grid[1], ['left'])
gl.unframe(grid[2], ['right'])
gl.unframe(grid[3], ['bottom', 'left'])
fig.subplots_adjust(hspace=0.0)

# plot GPS velocity
df = get_gps_velocity()
gl.rollplot(grid[0], df['vh'], 4*3, c='g')

# for each borehole
lines = [None, None]
for i, bh in enumerate(gl.boreholes):

    # plot pressure sensor water level
    df = get_pressure_wlev(bh)
    df.plot(ax=grid[1], c=gl.colors[i], lw=2.0)
    lines[i] = grid[1].get_lines()[-1]  # select last line for the legend

    # plot tilt unit water level
    df = get_tiltunit_wlev(bh)
    df.plot(ax=grid[1], c='k', alpha=0.2, legend=False)

    # plot tilt
    df = get_tiltunit_tilt(bh)
    df.plot(ax=grid[2], c=gl.colors[i], lw=0.1, legend=False)

    # plot temperature
    df = get_tempsens_temp(bh)
    df.plot(ax=grid[3], c=gl.colors[i], lw=0.1, legend=False)
    df = get_tiltunit_temp(bh)
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

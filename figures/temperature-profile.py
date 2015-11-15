#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import projectglobals as gl

boreholes = ['downstream', 'upstream']
colors = ['b', 'r']

def get_profiles(depth, temp):
    """Return avg, min and max temperature profile from data frame."""

    # remove sensors above the ground
    inicecols = depth < 0.0
    temp = temp[temp.columns[inicecols]]
    depth = depth[inicecols]

    # order by depth
    ordercols = np.argsort(depth)
    depth = depth[ordercols]
    temp = temp[ordercols]

    # extract values
    tmin = temp.min().values
    tavg = temp.mean().values
    tmax = temp.max().values
    z = depth.values

    return z, tmin, tavg, tmax

# dates to plot
start = '2014-10-15'
end = '2015-07-15'

# initialize figure
fig, grid = plt.subplots(1, 2, sharey=True)

# for each borehole
for i, bh in enumerate(boreholes):
    ax = grid[i]

    # read temperature values
    temp_temp = gl.load_data('thstring', 'temp', bh)
    tilt_temp = gl.load_data('tiltunit', 'temp', bh)

    # read depths
    temp_depth = gl.load_depth('thstring', bh)
    tilt_depth = gl.load_depth('tiltunit', bh)

    # FIXME
    tilt_depth *= -1
    tilt_temp *= 1e-3

    # resample and concatenate
    tilt_temp = tilt_temp.resample('1D')[start:end]
    temp_temp = temp_temp.resample('1D')[start:end]
    join_temp = pd.concat((temp_temp, tilt_temp), axis=1)
    join_depth = pd.concat((temp_depth, tilt_depth))

    # extract profiles
    temp_z, temp_tmin, temp_tavg, temp_tmax = get_profiles(temp_depth, temp_temp)
    tilt_z, tilt_tmin, tilt_tavg, tilt_tmax = get_profiles(tilt_depth, tilt_temp)
    join_z, join_tmin, join_tavg, join_tmax = get_profiles(join_depth, join_temp)

    # plot
    ax.fill_betweenx(join_z, join_tmin, join_tmax,
                     facecolor=colors[i], edgecolor='none', alpha=0.2)
    ax.plot(join_tavg, join_z, '-', c=colors[i])
    ax.plot(temp_tavg, temp_z, 'o', c=colors[i])
    ax.plot(tilt_tavg, tilt_z, '^', c=colors[i])
    ax.set_title(bh)

    # add horizontal lines
    ax.axhline(join_z[0], c='k')
    ax.axhline(0.0, c='k')

# save
fig.savefig('temperature-profile')

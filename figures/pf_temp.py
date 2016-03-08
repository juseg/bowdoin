#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut


def get_profiles(depth, temp):
    """Return avg, min and max temperature profile from data frame."""

    # remove sensors above the ground
    inicecols = depth > 0.0
    temp = temp[temp.columns[inicecols]]
    depth = depth[inicecols]

    # order by depth
    depth = depth.sort_values()
    temp = temp[depth.index.values]

    # extract values
    tmin = temp.min().values
    tavg = temp.mean().values
    tmax = temp.max().values
    z = depth.values

    return z, tmin, tavg, tmax

# dates to plot
start = '2014-11-01'
end = '2015-07-01'

# initialize figure
fig, ax = ut.pl.subplots_mm(nrows=1, ncols=1, sharex=True, sharey=True)

# for each borehole
base_depth = 0.0
for i, bh in enumerate(ut.boreholes):

    # read temperature values
    temp_temp = ut.io.load_data('thstring', 'temp', bh)
    tilt_temp = ut.io.load_data('tiltunit', 'temp', bh)

    # read depths
    temp_depth = ut.io.load_depth('thstring', bh).squeeze()
    tilt_depth = ut.io.load_depth('tiltunit', bh).squeeze()
    pres_depth = ut.io.load_depth('pressure', bh).squeeze()
    base_depth = max(base_depth, pres_depth)

    # sensors can't be lower than the base
    temp_depth = np.minimum(temp_depth, base_depth)

    # resample and concatenate
    tilt_temp = tilt_temp.resample('1D')[start:end]
    temp_temp = temp_temp.resample('1D')[start:end]
    #join_temp = pd.concat((temp_temp, tilt_temp), axis=1)
    #join_depth = pd.concat((temp_depth, tilt_depth))

    # extract profiles
    temp_z, temp_tmin, temp_tavg, temp_tmax = get_profiles(temp_depth, temp_temp)
    tilt_z, tilt_tmin, tilt_tavg, tilt_tmax = get_profiles(tilt_depth, tilt_temp)
    #join_z, join_tmin, join_tavg, join_tmax = get_profiles(join_depth, join_temp)

    # plot profiles
    ax.fill_betweenx(temp_z, temp_tmin, temp_tmax,
                     facecolor=ut.colors[i], edgecolor='none', alpha=0.25)
    ax.fill_betweenx(tilt_z, tilt_tmin, tilt_tmax,
                     facecolor='0.75', edgecolor='none', alpha=0.25)
    ax.plot(temp_tavg, temp_z, '-o', c=ut.colors[i], label=bh)
    ax.plot(tilt_tavg, tilt_z, '-^', c='0.75')

    # add base lines
    ax.axhline(base_depth, c='k')

# plot melting point
g = 9.80665     # gravity
rhoi = 910.0    # ice density
beta = 7.9e-8   # Luethi et al. (2002)
base_temp_melt = -beta * rhoi * g * base_depth
ax.plot([0.0, base_temp_melt], [0.0, base_depth], c='k', ls=':')

# add surface line
ax.axhline(0.0, c='k')

# set axes properties
ax.set_xlim(-12.0, 2.0)
ax.set_ylim(300.0, 0.0)
ax.set_xlabel(u'ice temperature averaged between %s and %s (°C)' %
              (start, end))
ax.set_ylabel('depth (m)')
ax.legend(loc='best')

# save
fig.savefig('pf_temp')

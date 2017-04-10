#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut


def get_profiles(depth, temp):
    """Return avg, min and max temperature profile from data frame."""

    # if dataset has several columns
    if len(temp.columns) > 1:

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
end = '2015-11-01'

# initialize figure
fig, ax = plt.subplots()

# for each borehole
base_depth = 0.0
for i, bh in enumerate(ut.boreholes):
    #if bh == 'downstream': continue

    # read temperature values
    temp = ut.io.load_all_temp(bh)[start:end]

    # read depths
    depth = ut.io.load_all_depth(bh)
    base_depth = max(base_depth, depth['pres'])

    # sensors can't be lower than the base
    depth = np.minimum(depth, base_depth)

    # extract profiles
    temp_z, temp_tmin, temp_tavg, temp_tmax = get_profiles(depth, temp)

    # plot profiles
    ax.fill_betweenx(temp_z, temp_tmin, temp_tmax,
                     facecolor=ut.colors[bh], edgecolor='none', alpha=0.25)
    ax.plot(temp_tavg, temp_z, '-o', c=ut.colors[bh], label=bh)

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
ax.set_xlim(-11.0, 1.0)
ax.set_ylim(275.0, 0.0)
ax.set_title(r'%s to %s' % (start, end))
ax.set_xlabel(u'ice temperature (°C)')
ax.set_ylabel('depth (m)')
ax.legend(loc='best')

# save
fig.savefig('pf_temp')

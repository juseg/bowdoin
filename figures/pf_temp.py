#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut


# dates to plot
start = '2015-01-01'
end = '2016-07-01'

# markers per sensor type
markers = dict(temp='o', unit='^')  #, pres='s')

# initialize figure
fig, ax = plt.subplots()

# for each borehole
base_depth = 0.0
for i, bh in enumerate(ut.boreholes):

    # read temperature and depth
    temp = ut.io.load_all_temp(bh)[start:end] #.dropna(axis=1, how='all')
    depth = ut.io.load_all_depth(bh)
    depth['temp01'] = depth['pres']
    base_depth = max(base_depth, depth['pres'])

    # order by depth, remove nulls and sensors above ground
    subglac = depth > 0.0
    notnull = depth.notnull() & temp.notnull().any()
    depth = depth[notnull&subglac].sort_values()
    temp = temp[depth.index.values]

    # extract profiles
    tmin = temp.min()
    tavg = temp.mean()
    tmax = temp.max()

    # plot profiles
    ax.fill_betweenx(depth, tmin, tmax,
                     facecolor=ut.colors[bh], edgecolor='none', alpha=0.25)
    ax.plot(tavg, depth, '-', c=ut.colors[bh], label=bh)
    for sensor, marker in markers.iteritems():
        cols = [s for s in temp.columns if s.startswith(sensor)]
        ax.plot(tavg[cols], depth[cols], marker, c=ut.colors[bh])

    # add base line
    ax.plot([tavg[-1]-0.5, tavg[-1]+0.5], [depth[-1], depth[-1]], c='k')

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

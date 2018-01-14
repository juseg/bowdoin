#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut


# dates to plot
dates = dict(upper=['2015-01-01', '2016-07-12'],
             lower=['2015-01-01', '2015-11-12', '2016-07-19'])
styles = ['-', ':', ':']

# markers per sensor type
markers = dict(temp='o', unit='^')  #, pres='s')

# initialize figure
fig, ax = plt.subplots()

# for each borehole
base_depth = 0.0
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[bh]

    # read temperature and depth data
    temp_depth = ut.io.load_depth('thstring', bh)
    tilt_depth = ut.io.load_depth('tiltunit', bh)
    pres_depth = ut.io.load_depth('pressure', bh)
    pres_depth.index = ['pres']
    manu_temp = ut.io.load_data('thstring', 'mantemp', bh)
    temp_temp = ut.io.load_data('thstring', 'temp', bh)
    tilt_temp = ut.io.load_data('tiltunit', 'temp', bh)

    # prepare depth profile
    depth = pd.concat((temp_depth, tilt_depth))
    subglac = depth > 0.0
    notnull = depth.notnull() #& temp.notnull()
    depth = depth[notnull&subglac].sort_values()

    # for each date to plot
    for date, ls in zip(dates[bh], styles):

        # prepare combined profiles
        if date in temp_temp.index:
            temp = temp_temp[date].mean()
        else:
            temp = manu_temp[date].squeeze()
        if date in tilt_temp.index:
            temp = temp.append(tilt_temp[date].mean())

        # order by depth, remove nulls and sensors above ground
        temp = temp[depth.index.values]

        # plot profiles
        label = '{}, {}'.format(bh, date)
        ax.plot(temp, depth, c=ut.colors[bh], ls=ls, label=label)
        if date == dates[bh][0]:
            for sensor, marker in markers.iteritems():
                cols = [s for s in temp.index if s.startswith(sensor)]
                ax.plot(temp[cols], depth[cols], marker, c=ut.colors[bh])

    # add base line
    ax.plot([temp['temp01']-0.5, temp['temp01']+0.5],
            [depth['temp01'], depth['temp01']], c='k')

    # compute maximum depth
    base_depth = max(base_depth, pres_depth.squeeze())

# plot melting point
g = 9.80665     # gravity
rhoi = 910.0    # ice density
beta = 7.9e-8   # Luethi et al. (2002)
base_temp_melt = -beta * rhoi * g * base_depth
ax.plot([0.0, base_temp_melt], [0.0, base_depth], c='k', ls=':')

# set axes properties
ax.invert_yaxis()
ax.set_xlabel(u'ice temperature (°C)')
ax.set_ylabel('depth (m)')
ax.legend(loc='lower left')

# save
ut.pl.savefig(fig)

#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut


# plot only if data between these dates
start = '2015-01-01'
end = '2016-07-01'

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(ut.boreholes):
    ax = grid[i]
    c = ut.colors[bh]

    # read tilt unit temperature and depth
    temp = ut.io.load_data('tiltunit', 'temp', bh)
    depth = ut.io.load_depth('tiltunit', bh)
    depth_pres = ut.io.load_depth('pressure', bh)
    depth['temp01'] = depth_pres

    # plot tilt unit temperature
    temp.plot(ax=ax, c='0.75', legend=False)

    # read thermistor string temperature and depth
    temp = ut.io.load_data('thstring', 'temp', bh)  #.resample('1D').mean()
    depth = ut.io.load_depth('thstring', bh)
    depth_pres = ut.io.load_depth('pressure', bh)
    depth['temp01'] = depth_pres

    # order by depth, remove nulls and sensors above ground
    subglac = depth > 0.0
    notnull = depth.notnull() & temp[start:end].notnull().any()
    depth = depth[notnull&subglac].sort_values()
    temp = temp[depth.index.values]
    temp.plot(ax=ax, c=c, legend=False)

    # read manual temperature
    temp = ut.io.load_data('thstring', 'mantemp', bh)

    # order by depth, remove nulls and sensors above ground
    temp = temp[depth.index.values]

    # plot manual temperature
    temp.plot(ax=ax, c=c, ls='', marker='o', legend=False)

    # set label
    ax.set_ylabel(bh)
    #ax.set_xlim('2016-07-10', '2016-07-20')

# save
ut.pl.savefig(fig)

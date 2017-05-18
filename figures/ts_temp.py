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

    # colors per sensor type
    colors = dict(temp=ut.colors[bh], unit='0.75')  #, pres='k')

    # read temperature and depth
    temp = ut.io.load_all_temp(bh, freq='1H')
    depth = ut.io.load_all_depth(bh)
    depth['temp01'] = depth['pres']

    # order by depth, remove nulls and sensors above ground
    subglac = depth > 0.0
    notnull = depth.notnull() & temp[start:end].notnull().any()
    depth = depth[notnull&subglac].sort_values()
    temp = temp[depth.index.values]

    # plot with different colors
    for sensor, c in colors.iteritems():
        cols = [s for s in temp.columns if s.startswith(sensor)]
        temp[cols].plot(ax=ax, c=c, legend=False)

    # set title
    ax.set_ylabel(bh)

# save
ut.pl.savefig(fig)

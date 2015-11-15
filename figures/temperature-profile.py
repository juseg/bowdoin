#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# dates to plot
date = '2015-02-01 00:00:00'

# initialize figure
fig, grid = plt.subplots(1, 2, sharey=True)

# for each borehole
for i, bh in enumerate(['downstream', 'upstream']):
    ax = grid[i]

    # read temperature values
    filename = 'data/processed/bowdoin-temperature-%s.csv' % bh
    temp_temp = pd.read_csv(filename, parse_dates=True, index_col='date')
    filename = 'data/processed/bowdoin-inclino-temp-%s.csv' % bh
    tilt_temp = pd.read_csv(filename, parse_dates=True, index_col='date')

    # read depths
    filename = 'data/processed/bowdoin-temperature-depth-%s.csv' % bh
    temp_depth = pd.read_csv(filename, header=None, index_col=0, squeeze=True)
    filename = 'data/processed/bowdoin-inclino-depth-%s.csv' % bh
    tilt_depth = pd.read_csv(filename, header=None, index_col=0, squeeze=True)

    # select date
    temp_temp = temp_temp.loc[date].values
    tilt_temp = tilt_temp.loc[date].values

    # FIXME
    tilt_depth *= -1
    tilt_temp *= 1e-3

    # order by depth and mask above surface
    order = np.argsort(temp_depth)
    temp_depth = temp_depth[order]
    temp_temp = np.ma.masked_where(temp_depth > 0.0, temp_temp[order])

    # plot
    ax.plot(temp_temp, temp_depth, 'o-')
    ax.plot(tilt_temp, tilt_depth, 'o-')
    ax.set_title(bh)

    # add horizontal lines
    ax.axhline(temp_depth[0], c='k')
    ax.axhline(0.0, c='k')

# save
fig.savefig('temperature-profile')

#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# dates to plot
targets = ['2014-%02d-25 06:00' % m for m in range(7, 13)]

# initialize figure
fig, grid = plt.subplots(1, 2, sharey=True)

# for each borehole
for i, bh in enumerate(['upstream', 'downstream']):
    ax = grid[i]
    filename = 'data/processed/bowdoin-temperature-%s.csv' % bh

    # calculate sensor depths
    if bh == 'downstream':
        depth = np.hstack([-243.7 + 20.0*np.arange(9),
                           -8.75 + 20.0*np.arange(-4,3)])
    if bh == 'upstream':
        depth = np.hstack([-265.3 + 20.0*np.arange(9),
                           -6.6 + 20.0*np.array([-5, -4, -3, -2, +1, -1, 0])])

    # read data
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # order columns by depth
    order = np.argsort(depth)

    # plot
    for tg in targets:
        row = df.index.searchsorted(tg)
        date = df.index[row]
        temp = df.iloc[row]
        ax.plot(temp[order], depth[order], '-', label=date)
        ax.set_title(bh)

    # add horizontal lines
    ax.axhline(depth[0], c='k')
    ax.axhline(0.0, c='k')

# save
ax.legend(loc='lower left')
fig.savefig('temperature-profile')

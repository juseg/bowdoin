#!/usr/bin/env python2

import datetime
import numpy as np
import matplotlib.pyplot as plt

# dates to plot
targets = [datetime.datetime(2014, m, 25, 6, 0) for m in range(7, 13)]

# date converter
mkdate = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

# initialize figure
fig, grid = plt.subplots(1, 2, sharey=True)

# parameters
for bh in [1, 2]:
    ax = grid[bh-1]
    filename = 'data/processed/bowdoin-temperature-bh%d.txt' % bh

    # calculate sensor depths
    if bh == 1:
        depth = np.hstack([-243.7 + 20.0*np.arange(9),
                           -8.75 + 20.0*np.arange(-4,3)])
    if bh == 2:
        depth = np.hstack([-265.3 + 20.0*np.arange(9),
                           -6.6 + 20.0*np.array([-5, -4, -3, -2, +1, -1, 0])])

    # check which 
    order = np.argsort(depth)


    # read in a record array
    a = np.genfromtxt(filename, delimiter=',',
                      names=True, #('date', 'pressure'),
                      converters={'date': mkdate},
                      dtype=None)

    # plot
    for tg in targets:
        row = np.searchsorted(a['date'], tg)
        date = a[row][0]
        temp = np.array([a[row][col] for col in range(1, 17)])
        ax.plot(temp[order], depth[order], '-', label=date)

    # add horizontal lines
    ax.axhline(depth[0], c='k')
    ax.axhline(0.0, c='k')

# save
ax.legend(loc='lower left')
fig.savefig('temperature-profile')

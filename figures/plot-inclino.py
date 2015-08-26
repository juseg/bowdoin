#!/usr/bin/env python2

import datetime
import numpy as np
import matplotlib.pyplot as plt

# date converter
mkdate = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# parameters
for bh in [1, 2]:
    ax = grid[bh-1]
    filename = 'data/processed/bowdoin-inclino-bh%d.txt' % bh

    # read in a record array
    a = np.genfromtxt(filename, delimiter=',',
                      missing_values=9999.0, usemask=True,
                      names=True, converters={'date': mkdate},
                      dtype=None)

    # plot
    for site in a.dtype.names[1:]:
        ax.plot_date(a['date'], a[site], '-')

    # set axes limits
    ax.set_ylim(0.0, 40.0)

# save
fig.savefig('plot-inclino')

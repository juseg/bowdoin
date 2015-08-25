#!/usr/bin/env python2

import datetime
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import date2num

# date converter
mkdate = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# parameters
for bh in [1, 2]:
    ax = grid[bh-1]
    filename = 'data/processed/bowdoin-temperature-bh%d.txt' % bh

    # read in a record array
    a = np.genfromtxt(filename, delimiter=',',
                      names=True, #('date', 'pressure'),
                      converters={'date': mkdate},
                      dtype=None)

    # plot
    for res in range(1, 17):
        ax.plot_date(a['date'], a['res%02d' % res], '-')

# save
fig.savefig('plot-temperature')

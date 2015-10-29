#!/usr/bin/env python2

import pandas as pd
import matplotlib.pyplot as plt

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# parameters
for bh in [1, 2]:
    ax = grid[bh-1]
    filename = 'data/processed/bowdoin-temperature-bh%d.txt' % bh

    # read in a record array
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # plot
    df.plot(ax=ax, legend=False)

# save
fig.savefig('plot-temperature')

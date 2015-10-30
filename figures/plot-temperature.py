#!/usr/bin/env python2

import pandas as pd
import matplotlib.pyplot as plt

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# for each borehole
for i, bh in enumerate(['upstream', 'downstream']):
    ax = grid[i]
    filename = 'data/processed/bowdoin-temperature-%s.csv' % bh

    # read in a record array
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # plot
    df.plot(ax=ax, legend=False, title=bh)

# save
fig.savefig('plot-temperature')

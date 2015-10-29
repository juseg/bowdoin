#!/usr/bin/env python2

import pandas as pd
import matplotlib.pyplot as plt

# initialize figure
fig, ax = plt.subplots(1, 1)

# loop on boreholes
for bh in [1, 2]:
    filename = 'data/processed/bowdoin-pressure-bh%d.txt' % bh

    # read in a record array
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # plot
    df['pressure'].plot(label='borehole %i' % bh)

# set axis limits
ax.set_ylim(175.0, 250.0)
ax.legend()

# save
fig.savefig('plot-pressure')

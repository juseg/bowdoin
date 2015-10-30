#!/usr/bin/env python2

import pandas as pd
import matplotlib.pyplot as plt

# initialize figure
fig, ax = plt.subplots(1, 1)

# for each borehole
for i, bh in enumerate(['upstream', 'downstream']):
    filename = 'data/processed/bowdoin-pressure-%s.csv' % bh

    # read in a record array
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # plot
    df['wlev'].plot(label=bh)

# set axis limits
ax.set_ylim(175.0, 250.0)
ax.legend()

# save
fig.savefig('plot-pressure')

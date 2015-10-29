#!/usr/bin/env python2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# initialize figure
fig, grid = plt.subplots(2, 1, sharex=True)

# parameters
for bh in [1, 2]:
    ax = grid[bh-1]
    filename = 'data/processed/bowdoin-inclino-bh%d.txt' % bh

    # read in a record array
    df = pd.read_csv(filename, parse_dates=True, index_col='date')

    # compute tilt
    axcols = [col for col in df.columns if col.startswith('ax')]
    aycols = [col for col in df.columns if col.startswith('ay')]
    tilt = pd.DataFrame()
    for xc, yc in zip(axcols, aycols):
        tc = xc.replace('ax', 'tilt')
        tilt[tc] = np.arcsin(np.sqrt(np.sin(df[xc])**2+np.sin(df[yc])**2))
        tilt[tc] *= 180/np.pi

    # plot
    tilt.plot(ax=ax)

# save
fig.savefig('plot-inclino')

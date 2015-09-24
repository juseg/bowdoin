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

    # compute tilt
    tiltx = np.ma.vstack([a[n] for n in a.dtype.names if 'ax' in n])
    tilty = np.ma.vstack([a[n] for n in a.dtype.names if 'ay' in n])
    tilt = np.arcsin(np.sqrt(np.sin(tiltx)**2+np.sin(tilty)**2))
    tilt = tilt*180/np.pi

    # plot
    ax.plot_date(a['date'], tiltx.T, '-')

# save
fig.savefig('plot-inclino')

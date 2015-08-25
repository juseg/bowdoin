#!/usr/bin/env python2

import datetime
import numpy as np
from matplotlib.pyplot import subplots

# initialize figure
fig, ax = subplots(1, 1, sharex=True)

# date converter
mkdate = lambda s: datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

# loop on boreholes
for bh in [1, 2]:
    filename = 'data/processed/bowdoin-pressure-bh%d.txt' % bh

    # read in a record array
    a = np.genfromtxt(filename, delimiter=',',
                      names=True, #('date', 'pressure'),
                      converters={'date': mkdate},
                      dtype=None)

    # plot
    ax.plot_date(a['date'], a['pressure'], '-', label='borehole %i' % bh)

# set axis limits
ax.set_ylim(175.0, 250.0)
ax.set_xlim(735400.0, 735800.0)
ax.legend()

# save
fig.savefig('plot-pressure')

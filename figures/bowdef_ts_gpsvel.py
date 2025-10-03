#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import bowdef_utils

# initialize figure
fig, ax = plt.subplots(1, 1)

# plot GPS velocity
c = bowdef_utils.colors['dgps']
ts = bowdef_utils.load_data('dgps', 'velocity', 'upper')['vh'].resample('15min').mean()
ts.plot(ax=ax, c=c, ls='', marker='.', markersize=0.5, alpha=0.25)
ts.resample('24h').mean().plot(ax=ax, c=c)
ax.set_ylim(-50.0, 1050.0)

# add label
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')

# save
bowdef_utils.savefig(fig)

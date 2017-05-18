#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, ax = plt.subplots(1, 1)

# plot GPS velocity
c = ut.colors['dgps']
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T').mean()
ts.plot(ax=ax, color=c, ls='', marker='.', markersize=0.5)
ts.resample('1D').mean().plot(ax=ax, c=c)

# add label
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')

# save
ut.pl.savefig(fig)

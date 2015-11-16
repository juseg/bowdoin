#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import projectglobals as gl

# initialize figure
fig, ax = plt.subplots(1, 1)

# plot GPS velocity
ts = gl.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')
gl.rollplot(ax, ts, 4*3, c='g')

# add label
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')

# save
fig.savefig('ts_gpsv')

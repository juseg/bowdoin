#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd
import util as ut

# initialize figure
fig, ax = plt.subplots(1, 1)

# plot sentinel velocity 12 day
c = ut.palette[8]
df = pd.read_csv('data/satellite/bowdoin-sentinel-12day.txt',
                 parse_dates=['start', 'end'])
dt = df['end']-df['start']
mid = df['start'] + dt/2
vel = df['velocity']
err = df['error']
ax.errorbar(mid, vel, xerr=dt/2, yerr=err, c=c, ls='', zorder=3)

# plot sentinel velocity 24 day
c = ut.palette[9]
df = pd.read_csv('data/satellite/bowdoin-sentinel-24day.txt',
                 parse_dates=['start', 'end'])
dt = df['end']-df['start']
mid = df['start'] + dt/2
vel = df['velocity']
err = df['error']
ax.errorbar(mid, vel, xerr=dt/2, yerr=err, c=c, ls='', zorder=3)

# plot GPS velocity
c = ut.colors[2]
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')
ts.plot(ax=ax, color=c, ls='', marker='.', markersize=0.5)
ts.resample('1D').plot(ax=ax, c=c)

# add label
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')
ax.set_ylim(0.0, 800.0)
fig.autofmt_xdate()

# save
fig.savefig('sentinel')

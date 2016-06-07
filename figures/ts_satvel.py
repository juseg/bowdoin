#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd
import util as ut
import scipy.io

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

# plot landsat velocity
c = ut.palette[11]
mat = scipy.io.loadmat('data/satellite/bowdoin-landsat.mat')
start = ['2014-07-13', '2014-09-06', '2014-10-01', '2015-04-02', '2015-06-14']
start = pd.to_datetime(start).values  #, unit='D').values
end = ['2014-09-06', '2014-10-01', '2015-03-06', '2015-05-20', '2015-08-01']
end = pd.to_datetime(end).values  #, unit='D').values
dt = end - start
mid = start + dt/2
vel = mat['V'][0]*365.0
err = mat['S'][0]*365.0
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
fig.savefig('ts_satvel')

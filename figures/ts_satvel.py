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

# plot new sentinel velocity
df = pd.read_csv('data/satellite/bowdoin-sentinel.txt', delimiter=',\s+',
                 index_col='YYYY-MM-DD (avg)', parse_dates=True)
dt = pd.to_timedelta(df['time-diff (days)'], unit='D')
mid = df.index
vel = df['vel (m/a)']
err = df['vel_error (m/a)']
mask = (dt <= pd.to_timedelta('12D'))
ax.errorbar(mid[mask], vel[mask], xerr=dt[mask]/2, yerr=err[mask],
            c=ut.palette[6], ls='', lw=0.5, zorder=3)
ax.errorbar(mid[-mask], vel[-mask], xerr=dt[-mask]/2, yerr=err[-mask],
            c=ut.palette[7], ls='', lw=0.5, zorder=3)

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

# plot deformation velocity
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[i]

    # load data
    exz = ut.io.load_strain_rate(bh, '1D')['2014-11':]
    depth = ut.io.load_depth('tiltunit', bh).squeeze()
    depth_base = ut.io.load_depth('pressure', bh).squeeze()

    # ignore two lowest units on upstream borehole
    if bh == 'upstream':
        broken = ['unit02', 'unit03']
        depth.drop(broken, inplace=True)
        exz.drop(broken, axis='columns', inplace=True)

    # fit to a Glen's law
    n, A = ut.al.glenfit(depth, exz.T)

    # calc deformation velocity
    vdef = ut.al.vsia(0.0, depth_base, n, A)
    vdef = pd.Series(index=exz.index, data=vdef)

    # plot
    vdef.plot(ax=ax, c=c, label=bh)

# plot GPS velocity
c = ut.colors[2]
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')
ts.plot(ax=ax, color=c, ls='', marker='.', markersize=0.5)
ts.resample('1D').plot(ax=ax, c=c)

# add field campaigns
ax.axvspan('2014-07-15', '2014-07-29', ec='none', fc=ut.palette[7], alpha=0.25)
ax.axvspan('2015-07-06', '2015-07-20', ec='none', fc=ut.palette[7], alpha=0.25)
ax.axvspan('2016-07-04', '2016-07-25', ec='none', fc=ut.palette[7], alpha=0.25)

# add label
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')
ax.set_xlim('2014-07-01', '2016-08-01')
ax.set_ylim(0.0, 800.0)
fig.autofmt_xdate()

# save
fig.savefig('ts_satvel')

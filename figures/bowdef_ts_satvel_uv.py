#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import pandas as pd
import util as ut

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(135.0, 80.0),
                            left=10.0, right=2.5, bottom=10.0, top=2.5)

# plot new sentinel velocity
df = pd.read_csv('../data/satellite/bowdoin-sentinel.txt', delimiter=',\s+',
                 index_col='YYYY-MM-DD (avg)', parse_dates=True,
                 engine='python')
dt = pd.to_timedelta(df['time-diff (days)'], unit='D')
mid = df.index
vel = df['vel (m/a)']
err = df['vel_error (m/a)']
mask = (dt <= pd.to_timedelta('12D'))
ax.errorbar(mid[mask], vel[mask], xerr=dt[mask]/2, yerr=err[mask],
            c=ut.palette['lightpurple'], ls='', lw=0.5, zorder=4, alpha=0.75)
ax.errorbar(mid[-mask], vel[-mask], xerr=dt[-mask]/2, yerr=err[-mask],
            c=ut.palette['darkpurple'], ls='', lw=0.5, zorder=4, alpha=0.75)

# plot landsat velocity
df = pd.read_csv('../data/satellite/bowdoin-landsat-uv.csv',
                 parse_dates=['start', 'end'])
dt = df['end'] - df['start']
mid = df['start'] + dt/2
vel = df['vel']
err = df['err']
mid = pd.DatetimeIndex(mid)
ax.errorbar(mid, vel, xerr=dt/2, yerr=err,
            c=ut.palette['darkorange'], lw=0.5, ls='', zorder=3, alpha=0.75)

# plot deformation velocity
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[bh]

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
c = ut.colors['dgps']
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T').mean()
ts.plot(ax=ax, c=c, ls='', marker='.', markersize=0.5, alpha=0.25)
ts.resample('1D').mean().plot(ax=ax, c=c)

# add annotations
kwa = dict(fontweight='bold', ha='center', va='center')
ax.text('20150801', 600, 'GPS', color=ut.colors['dgps'], **kwa)
ax.text('20150501', 250, 'Landsat', color=ut.palette['darkorange'], **kwa)
ax.text('20160201', 450, 'Sentinel-1', color=ut.palette['darkpurple'], **kwa)
ax.text('20150201', 100, 'Boreholes', color=ut.colors['upstream'], **kwa)

# add field campaigns
ut.pl.plot_campaigns(ax)

# add label
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)')
ax.set_xlim('2014-07-01', '2017-08-01')
ax.set_ylim(0.0, 800.0)
#fig.autofmt_xdate()

# save
ut.pl.savefig(fig)

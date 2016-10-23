#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(135.0, 80.0),
                            left=10.0, right=10.0, bottom=10.0, top=2.5)

# for each borehole
lines = []
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[bh]

    # plot lowest tilt unit water level
    ts = ut.io.load_data('tiltunit', 'wlev', bh).resample('30T').mean().iloc[:,0]
    ts.plot(ax=ax, c='0.75', legend=False)

    # plot pressure sensor water level
    ts = ut.io.load_data('pressure', 'wlev', bh).resample('30T').mean()
    ts = ts.iloc[2:]  # remove the first hour corresponding to drilling
    ts.plot(ax=ax, c=ut.colors[bh], legend=False)
    lines.append(ax.get_lines()[-1])  # select last line for the legend

# add field campaigns
ut.pl.plot_campaigns(ax, y=350.0)

# add labels
kwa = dict(fontweight='bold', ha='left', va='center')
ax.text('20141001', 235, 'downstream water level', color=ut.colors['downstream'], **kwa)
ax.text('20140901', 200, 'upstream water level', color=ut.colors['upstream'], **kwa)
ax.set_ylabel('water level (m)', color=ut.palette['darkblue'], **kwa)

# add twin axes
ax = ax.twinx()

# plot GPS velocity
c = ut.colors['dgps']
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T').mean()
ts.plot(ax=ax, c=c, ls='', marker='.', markersize=0.5)
ts.resample('1D').mean().plot(ax=ax, c=c)

# add labels and set limits
ax.text('20150801', 600, 'GPS velocity', color=c, **kwa)
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)', color=ut.colors['dgps'], labelpad=0.0)
ax.set_xlim('2014-07', '2016-08')
ax.set_ylim(0, 800)

# save
fig.savefig('ts_combined')

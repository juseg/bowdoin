#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, ax = plt.subplots(1, 1)

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
ax.axvspan('2014-07-15', '2014-07-29', ec='none', fc=ut.palette['darkorange'], alpha=0.25)
ax.axvspan('2015-07-06', '2015-07-20', ec='none', fc=ut.palette['darkorange'], alpha=0.25)

# add labels
ax.text('20140901', 230, 'downstream water level', color=ut.colors['downstream'])
ax.text('20140801', 200, 'upstream water level', color=ut.colors['upstream'])
ax.set_ylabel('water level (m)', color=ut.palette['darkblue'])

# add twin axes
ax = ax.twinx()

# plot GPS velocity
c = ut.colors['dgps']
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T').mean()
ts.plot(ax=ax, c=c, ls='', marker='.', markersize=0.5)
ts.resample('1D').mean().plot(ax=ax, c=c)

# add labels and set limits
ax.text('20150515', 750, 'GPS velocity', color=c)
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)', color=ut.colors['dgps'], labelpad=0.0)
ax.set_xlim('2014-07-14', '2015-07-21')
ax.set_ylim(-200, 1200)

# save
fig.savefig('ts_combined')

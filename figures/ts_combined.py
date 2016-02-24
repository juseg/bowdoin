#!/usr/bin/env python2
# coding: utf-8

import matplotlib.pyplot as plt
import util as ut

# initialize figure
fig, ax = plt.subplots(1, 1)

# for each borehole
lines = []
for i, bh in enumerate(ut.boreholes):
    c = ut.colors[i]

    # plot lowest tilt unit water level
    ts = ut.io.load_data('tiltunit', 'wlev', bh).resample('30T').iloc[:,0]
    ts.plot(ax=ax, c='0.75', legend=False)

    # plot pressure sensor water level
    ts = ut.io.load_data('pressure', 'wlev', bh).resample('30T')
    ts = ts.iloc[2:]  # remove the first hour corresponding to drilling
    ts.plot(ax=ax, c=ut.colors[i], legend=False)
    lines.append(ax.get_lines()[-1])  # select last line for the legend

# add field campaigns
ax.axvspan('2014-07-15', '2014-07-29', ec='none', fc=ut.palette[7], alpha=0.25)
ax.axvspan('2015-07-06', '2015-07-20', ec='none', fc=ut.palette[7], alpha=0.25)

# add label and legend
ax.set_ylabel('water level (m)')
ax.legend(lines, ut.boreholes, loc='lower right')

# add twin axes
ax = ax.twinx()

# plot GPS velocity
c = ut.colors[2]
ts = ut.io.load_data('dgps', 'velocity', 'upstream')['vh'].resample('15T')
ts.plot(ax=ax, c=c, ls='', marker='.', markersize=0.5)
ts.resample('1D').plot(ax=ax, c=c)

# add label and set limits
ax.set_ylabel(r'horizontal velocity ($m\,a^{-1}$)', labelpad=0.0)
ax.set_xlim('2014-07-14', '2015-07-21')
ax.set_ylim(-200, 1200)

# save
fig.savefig('ts_combined')

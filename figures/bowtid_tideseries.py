#!/usr/bin/env python2
# coding: utf-8


import util as ut

# initialize figure
fig, grid = ut.pl.subplots_mm(figsize=(150.0, 75.0), nrows=1, ncols=2,
                              sharex=False, sharey=False, wspace=12.5,
                              left=10.0, right=2.5, bottom=10.0, top=2.5)

# load Thule and Bowdoin tide data
thul = ut.io.load_tide_thul(start='2015-07', end='2015-08')
bowd = ut.io.load_tide_bowd()

# crop Thule data and downsample Bowdoin
thul = thul[bowd.index[0]:bowd.index[-1]]
bowd = bowd.reindex_like(thul, method='nearest')

# plot time series
ax = grid[0]
thul.plot(ax=ax, label='Pituffik tide')
bowd.plot(ax=ax, label='Bowdoin tide')
ax.set_xlabel('Date', labelpad=-8.0)
ax.set_ylabel('Tide', labelpad=0.0)
ax.legend()

# plot scatter plot
ax = grid[1]
ax.scatter(thul, bowd, marker='+', alpha=0.25)
ax.set_xlabel('Pituffik tide')
ax.set_ylabel('Bowdoin tide', labelpad=0.0)

# save
ut.pl.savefig(fig)
#ax.set_visible(False)
#ut.pl.savefig(fig, suffix='_z0')

#!/usr/bin/env python2
# coding: utf-8

import util as ut

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(85.0, 65.0),
                            left=12.0, right=1.5, bottom=9.0, top=1.5)

# plot tilt unit water level
p = ut.io.load_bowtid_data('wlev').resample('1H').mean()
p.plot(ax=ax)

## plot pressure sensor water level
#for i, bh in enumerate(ut.boreholes):
#    ts = ut.io.load_data('pressure', 'wlev', bh).resample('1H').mean()
#    ts = ts.iloc[2:]  # remove the first hour corresponding to drilling
#    ts.plot(ax=ax, c='k', ls=['--', ':'][i], lw=1.0, alpha=0.75)

# add label
ax.set_ylabel('pressure head (m w.e.)')
ax.legend(ncol=3)

# save
ut.pl.savefig(fig)

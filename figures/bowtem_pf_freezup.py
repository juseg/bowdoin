#!/usr/bin/env python2
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import util as ut

# physical constants
g = 9.80665     # gravity
rhoi = 910.0    # ice density
beta = 7.9e-8   # 7.9e-8 Luethi et al. (2002)

# initialize figure
fig, ax = ut.pl.subplots_mm(figsize=(85.0, 75.0), nrows=1, ncols=1,
                            sharex=False, sharey=True, wspace=2.5,
                            left=10.0, right=2.5, bottom=10.0, top=2.5)

# load data
t, z = ut.io.load_bowtem_data()
z = z.iloc[0]
t = t['20140723':'20140801'].resample('1D').mean()

# plot profiles
# FIXME sensors below the base
bholes = ['U', 'L']
colors = ['C0', 'C1']
for b, c in zip(bholes, colors):
    cols = z[z.index.str.startswith(b)].index.values
    mark = [dict(P='s', T='o', I='^')[col[1]] for col in cols]
    ax.plot(t[cols].T, z[cols], c=c, marker='o')

# plot melting poit
melt = -beta * rhoi * g * z
ax.plot(melt, z, c='k', ls=':')

# plot ice base
for base in [248.0, 258.0, 268.0]:
    ax.axhline(base, c='k', lw=0.5)

# set axes properties
ax.invert_yaxis()
ax.set_xlabel(u'ice temperature (°C)')
ax.set_ylabel('depth (m)')

# save
ut.pl.savefig(fig)
